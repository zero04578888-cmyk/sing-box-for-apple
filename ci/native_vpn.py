"""Identity and two-component boundaries for this native VPN distribution.

Group authorization is user-reported for the MAIN app only. This does not grant
the extension a profile, change Apple's authorization, or authorize installation.
"""
import json
from pathlib import Path
import plistlib
import re

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = json.loads((ROOT / "ci/native_vpn_identity.json").read_text())
MINIMAL_ENTITLEMENTS = {
    "com.apple.developer.networking.networkextension": ["packet-tunnel-provider"],
    "com.apple.security.application-groups": ["$(APP_GROUP_IDENTIFIER)"],
}


def validate_identity(base, group):
    if base != IDENTITY["baseBundleID"]:
        raise ValueError("Native VPN main Bundle ID must match the user-specified identity.")
    if group != IDENTITY["appGroup"]:
        raise ValueError("App Group must be the exact user-reported authorized value; no generated placeholder is allowed.")
    if IDENTITY["vpnExtensionBundleID"] != base + ".extension":
        raise ValueError("Packet Tunnel identifier must match AppConfiguration's derived provider ID.")


def project_objects(text):
    # This project's stable OpenStep top-level object layout; not a general PBX parser.
    return dict(re.findall(r"\t\t([0-9A-F]{24}) /\* [^\n]*? \*/ = \{\n(.*?)\n\t\t\};", text, re.S))


def references(body, field):
    match = re.search(rf"\b{field} = \((.*?)\);", body, re.S)
    return re.findall(r"\b[0-9A-F]{24}\b", match[1]) if match else []


def validate_sources(root=ROOT):
    text = (root / "sing-box.xcodeproj/project.pbxproj").read_text()
    objects = project_objects(text)
    pending = ["3AEC20F22A459AB400A63465"]
    seen = set()
    names = set()
    while pending:
        target = pending.pop()
        if target in seen:
            continue
        seen.add(target)
        body = objects[target]
        names.add(re.search(r"\bname = ([^;]+);", body)[1].strip('"'))
        for dependency in references(body, "dependencies"):
            pending.append(re.search(r"\btarget = ([0-9A-F]{24})\b", objects[dependency])[1])
    if names != {"SFI", "Extension", "Library", "ApplicationLibrary"}:
        raise ValueError(f"Unexpected SFI dependency closure: {sorted(names)}")
    embedded = []
    for phase in references(objects["3AEC20F22A459AB400A63465"], "buildPhases"):
        body = objects[phase]
        if "isa = PBXCopyFilesBuildPhase;" in body and re.search(r"dstSubfolderSpec = (?:13|16);", body):
            for build_file in references(body, "files"):
                reference = re.search(r"\bfileRef = ([0-9A-F]{24})", objects.get(build_file, ""))
                # Single-line PBXBuildFile objects are intentionally inspected directly.
                if not reference:
                    reference = re.search(rf"{build_file} /\* [^\n]+?fileRef = ([0-9A-F]{{24}})", text)
                embedded.append(reference[1])
    if embedded != ["3A096F862A4ED3DE00D4A2ED"]:
        raise ValueError(f"Only Packet Tunnel may be embedded by SFI: {embedded}")
    for file in ["SFI/SFI.entitlements", "Extension/Extension.entitlements"]:
        if plistlib.loads((root/file).read_bytes()) != MINIMAL_ENTITLEMENTS:
            raise ValueError(f"Unexpected optional entitlement in native VPN target: {file}")
    for file in ["SFI/Info.plist", "Extension/Info.plist"]:
        info = plistlib.loads((root/file).read_bytes())
        if info.get("NebulaNativeVPNOnly") is not True or "NSUbiquitousContainers" in info:
            raise ValueError(f"Native marker/iCloud metadata mismatch: {file}")
    for uuid in ["3AEC20CB2A45991900A63465", "3AEC20CC2A45991900A63465"]:
        body = objects[uuid]
        base = re.search(r"\bBASE_PACKAGE_IDENTIFIER = ([^;]+);", body)[1].strip('"')
        group = re.search(r"\bAPP_GROUP_IDENTIFIER = ([^;]+);", body)[1].strip('"')
        validate_identity(base, group)
    return {"targets": sorted(names), "embeddedExtensions": 1, "requiredProfiles": 2,
            "identity": IDENTITY, "extensionProfileStatus": "MISSING"}


if __name__ == "__main__":
    print(json.dumps(validate_sources(), indent=2))
