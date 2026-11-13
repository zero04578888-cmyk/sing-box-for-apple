"""Validate and preserve a complete, isolated iOS app before creating an unsigned IPA.

No certificate, provisioning profile, account, device, or subscription input is accepted.
Requested entitlement templates are NOT signed entitlements or evidence of authorization.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess

EXTENSIONS = {
    "Extension": "extension",
    "WidgetExtension": "widget",
    "FileProviderExtension": "fileprovider",
    "ShareExtension": "share",
    "ActionExtension": "action",
    "IntentsExtension": "intents",
}
UPSTREAM = "io.nekohasekai.sfamt"
FORBIDDEN = {".p12", ".pfx", ".p8", ".key", ".mobileprovision", ".provisionprofile"}
PRIVATE_PEM = re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----\s+[A-Za-z0-9+/=\r\n]{32,}-----END (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----")


def read_plist(path):
    with path.open("rb") as stream:
        return plistlib.load(stream)


def check_public_tree(root):
    """Reject signing material and symlinks escaping a self-contained artifact."""
    root = root.resolve()
    for path in root.rglob("*"):
        if path.suffix.lower() in FORBIDDEN or path.name in {".env", "embedded.mobileprovision"} or path.name.startswith(".env."):
            raise ValueError(f"Signing material/private environment file is forbidden: {path.relative_to(root)}")
        if path.is_symlink() and not path.resolve().is_relative_to(root):
            raise ValueError(f"External symlink in artifact: {path.relative_to(root)}")
        if path.is_file() and not path.is_symlink() and path.stat().st_size < 2_000_000:
            if PRIVATE_PEM.search(path.read_bytes()):
                raise ValueError(f"Private key block in artifact: {path.relative_to(root)}")


def inventory(app, base, group):
    if not re.fullmatch(r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+){2,}", base):
        raise ValueError("A concrete reverse-DNS base identifier is required.")
    if base == UPSTREAM or base.startswith(UPSTREAM + ".") or group == "group." + UPSTREAM:
        raise ValueError("Upstream identity/container is forbidden for the side-by-side delivery.")
    check_public_tree(app)
    paths = [app, *sorted(app.rglob("*.appex"))]
    expected = {base, *(f"{base}.{suffix}" for suffix in EXTENSIONS.values())}
    actual = set()
    result = []
    for bundle in paths:
        info = read_plist(bundle / "Info.plist")
        identifier = info.get("CFBundleIdentifier")
        if identifier in actual:
            raise ValueError(f"Duplicate bundle identifier: {identifier}")
        actual.add(identifier)
        executable = info.get("CFBundleExecutable", "")
        if not executable or not (bundle / executable).is_file():
            raise ValueError(f"Missing executable for {bundle.name}")
        if info.get("CFBundleSupportedPlatforms") != ["iPhoneOS"]:
            raise ValueError(f"Not an iOS device bundle: {bundle.name}")
        if info.get("BasePackageIdentifier") != base or info.get("AppGroupIdentifier") != group:
            raise ValueError(f"Inconsistent runtime identity/App Group: {bundle.name}")
        point = info.get("NSExtension", {}).get("NSExtensionPointIdentifier") or info.get("EXAppExtensionAttributes", {}).get("EXExtensionPointIdentifier")
        if identifier == base + ".extension" and point != "com.apple.networkextension.packet-tunnel":
            raise ValueError("Packet Tunnel extension point is missing.")
        if bundle == app:
            if info.get("BGTaskSchedulerPermittedIdentifiers") != [base + ".update_profiles"]:
                raise ValueError("Background-task identifier does not match runtime identity.")
            if set(info.get("NSUbiquitousContainers", {})) != {"iCloud." + base}:
                raise ValueError("iCloud document container still uses a different identity.")
        result.append({"path": "." if bundle == app else bundle.relative_to(app).as_posix(),
                       "bundleID": identifier, "executable": executable, "extensionPoint": point,
                       "basePackageIdentifier": base, "appGroup": group,
                       "minimumOSVersion": info.get("MinimumOSVersion"), "requiresProvisioningProfile": True})
    if actual != expected:
        raise ValueError(f"Incomplete/unexpected app-extension set: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    return result


def expand(value, settings):
    if isinstance(value, list):
        return [expand(item, settings) for item in value]
    if isinstance(value, dict):
        return {expand(key, settings): expand(item, settings) for key, item in value.items()}
    if isinstance(value, str):
        for _ in range(10):
            updated = re.sub(r"\$\(([^)]+)\)", lambda match: str(settings.get(match[1], match[0])), value)
            if updated == value:
                break
            value = updated
        if "$(" in value:
            raise ValueError(f"Unresolved entitlement setting: {value}")
    return value


def inspect_macho(app):
    records = []
    binaries = []
    # Magic identifies code even when a dylib has an unconventional file name.
    magic = {b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca", b"\xca\xfe\xba\xbf"}
    for path in sorted(app.rglob("*")):
        if path.is_file() and not path.is_symlink():
            with path.open("rb") as stream:
                if stream.read(4) in magic:
                    binaries.append(path)
    for binary in binaries:
        archs = subprocess.check_output(["xcrun", "lipo", "-archs", str(binary)], text=True).strip().split()
        if "arm64" not in archs or "x86_64" in archs:
            raise ValueError(f"Invalid device architectures: {binary.relative_to(app)} {archs}")
        load_commands = subprocess.check_output(["xcrun", "otool", "-l", str(binary)], text=True)
        # iOS Simulator also runs arm64: architecture alone is not device proof.
        if not (re.search(r"platform\s+(?:IOS|2)\s", load_commands) or "LC_VERSION_MIN_IPHONEOS" in load_commands):
            raise ValueError(f"Not an iOS device Mach-O: {binary.relative_to(app)}")
        dependencies = []
        for line in subprocess.check_output(["xcrun", "otool", "-L", str(binary)], text=True).splitlines()[1:]:
            dependency = line.strip().split(" (compatibility version", 1)[0]
            dependencies.append(dependency)
            if dependency.startswith("@rpath/"):
                suffix = dependency.removeprefix("@rpath/")
                # Each extension can use its container's Frameworks; framework own-ID is in otool -L.
                candidates = [app / "Frameworks" / suffix, binary.parent / suffix]
                candidates += [parent / "Frameworks" / suffix for parent in binary.parents if parent.is_relative_to(app)]
                candidates += [path for path in binaries if path.as_posix().endswith("/" + suffix)]
                if not any(path.exists() for path in candidates) and not suffix.startswith("libswift"):
                    raise ValueError(f"Missing embedded dependency {dependency} for {binary.relative_to(app)}")
            elif not dependency.startswith(("/System/Library/", "/usr/lib/", "@loader_path/", "@executable_path/")):
                raise ValueError(f"Unexpected dependency path: {dependency}")
        signature = subprocess.run(["codesign", "-d", "-v", str(binary)], text=True, capture_output=True)
        records.append({"path": binary.relative_to(app).as_posix(), "architectures": archs,
                        "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "dependencies": dependencies,
                        "signatureInspection": (signature.stdout + signature.stderr).strip()})
    if not binaries:
        raise ValueError("No Mach-O binaries found.")
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--build-settings", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    settings = {entry["target"]: entry["buildSettings"] for entry in json.loads(args.build_settings.read_text())}
    base = settings["SFI"]["BASE_PACKAGE_IDENTIFIER"]
    group = settings["SFI"]["APP_GROUP_IDENTIFIER"]
    apps = inventory(args.app, base, group)
    code = inspect_macho(args.app)
    args.output.mkdir(parents=True, exist_ok=True)
    entitlements_dir = args.output / "requested-entitlements"
    entitlements_dir.mkdir(exist_ok=True)
    for target in ["SFI", *EXTENSIONS]:
        target_settings = settings[target]
        entitlements = expand(read_plist(root / target_settings["CODE_SIGN_ENTITLEMENTS"]), target_settings)
        if entitlements.get("com.apple.security.application-groups") != [group]:
            raise ValueError(f"Inconsistent requested App Group: {target}")
        if target in {"SFI", "Extension"} and "packet-tunnel-provider" not in entitlements.get("com.apple.developer.networking.networkextension", []):
            raise ValueError(f"Missing requested packet-tunnel-provider: {target}")
        (entitlements_dir / (target_settings["PRODUCT_BUNDLE_IDENTIFIER"] + ".requested.plist")).write_bytes(plistlib.dumps(entitlements))
    report = {"commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
              "runID": os.environ.get("GITHUB_RUN_ID"), "configuration": "Release", "platform": "iPhoneOS",
              "packaging": "Manual Payload IPA from unsigned device build; not xcodebuild -exportArchive",
              "developerSigning": "NOT_PERFORMED", "deviceVPNValidation": "NOT_PERFORMED",
              "placeholderIdentity": True, "mainBundleID": base, "vpnBundleID": base + ".extension", "appGroup": group,
              "requiredProfileCount": len(apps), "bundles": apps, "machO": code,
              "frameworks": [path.relative_to(args.app).as_posix() for path in sorted(args.app.rglob("*.framework"))],
              "swiftSystemLibraries": "Unbundled libswift dependencies are supplied by the supported iOS runtime; actual loading requires device validation."}
    (args.output / "release-inventory.json").write_text(json.dumps(report, indent=2) + "\n")
    payload = args.output / "ipa-staging" / "Payload"
    payload.mkdir(parents=True, exist_ok=True)
    shutil.copytree(args.app, payload / args.app.name, symlinks=True)
    ipa = args.output / "NEBULA-Release-Unsigned.ipa"
    subprocess.run(["ditto", "-c", "-k", "--norsrc", "--keepParent", str(payload), str(ipa)], check=True)
    (args.output / "SHA256SUMS.txt").write_text(f"{hashlib.sha256(ipa.read_bytes()).hexdigest()}  {ipa.name}\n")
    check_public_tree(args.output)
    print(f"Created {ipa.name}: {len(apps)} provisioning-profile-bearing bundles, {len(code)} Mach-O binaries; no developer signing.")


if __name__ == "__main__":
    main()
