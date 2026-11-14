"""Collect audited unsigned outputs, including failure logs; never accepts signed IPAs/profiles."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile

from package_unsigned_release import check_public_tree

ARCHIVE = Path("build/NEBULA-NativeVPN-StartupFix-Unsigned.xcarchive")
APP = ARCHIVE / "Products/Applications/sing-box.app"
EXPECTED_CODE = {"sing-box", "PlugIns/Extension.appex/Extension", "Frameworks/Library.framework/Library"}


def uuid_pairs(text):
    pairs = re.findall(r"UUID: ([0-9A-Fa-f-]{36}) \(([^)]+)\)", text)
    if not pairs:
        raise ValueError("Missing Mach-O UUID/architecture evidence")
    return {(uuid.lower(), arch) for uuid, arch in pairs}


def require_matching_uuids(binary, dwarf):
    if uuid_pairs(binary) != uuid_pairs(dwarf):
        raise ValueError("Binary and dSYM UUID/architecture mismatch")


def dwarf_path(archive, relative):
    if relative not in EXPECTED_CODE:
        raise ValueError(f"Unexpected executable path: {relative}")
    parts = Path(relative).parts
    owner = next((part for part in parts if part.endswith((".framework", ".appex"))), "sing-box.app")
    return archive / "dSYMs" / (owner + ".dSYM") / "Contents/Resources/DWARF" / parts[-1]


def verify_symbols(archive, app, inventory):
    if {code["path"] for code in inventory["machO"]} != EXPECTED_CODE or len(inventory["machO"]) != 3:
        raise ValueError("Expected exactly the main App, Packet Tunnel and Library Mach-O files")
    rows = []
    for code in inventory["machO"]:
        binary = app / code["path"]
        dwarf = dwarf_path(archive, code["path"])
        if not binary.is_file() or not dwarf.is_file():
            raise ValueError(f"Missing executable or corresponding dSYM: {code['path']}")
        binary_uuid = subprocess.check_output(["xcrun", "dwarfdump", "--uuid", str(binary)], text=True)
        dwarf_uuid = subprocess.check_output(["xcrun", "dwarfdump", "--uuid", str(dwarf)], text=True)
        require_matching_uuids(binary_uuid, dwarf_uuid)
        signature = subprocess.run(["codesign", "-d", "--verbose=2", str(binary)], text=True, capture_output=True)
        if signature.returncode == 0 or "not signed at all" not in signature.stdout + signature.stderr:
            raise ValueError(f"Unsigned code requirement not established: {code['path']}")
        rows.append({"binary": code["path"], "dwarf": dwarf.relative_to(archive).as_posix(),
                     "uuids": sorted(uuid_pairs(binary_uuid)),
                     "binarySHA256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                     "dwarfSHA256": hashlib.sha256(dwarf.read_bytes()).hexdigest()})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exit-status", type=int, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    # Nothing is staged for Codemagic upload unless all existing output trees pass this gate.
    for path in (Path("dist"), Path("build-logs"), ARCHIVE, Path("build/Release-Archive.xcresult")):
        if path.exists():
            check_public_tree(path)
    evidence_error = None
    symbols = []
    if args.exit_status == 0:
        try:
            inventory = json.loads(Path("dist/release-inventory.json").read_text())
            symbols = verify_symbols(ARCHIVE, APP, inventory)
            if not Path("dist/NEBULA-NativeVPN-Unsigned.ipa").is_file():
                raise ValueError("Missing validated unsigned IPA")
        except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
            evidence_error = str(error)
    success = args.exit_status == 0 and evidence_error is None
    public = Path("codemagic-artifacts")
    public.mkdir(exist_ok=False)  # Refuse mixed outputs from two attempts in one checkout.
    if Path("build-logs").exists():
        shutil.copytree("build-logs", public / "build-logs")
    if success:
        shutil.copyfile("dist/NEBULA-NativeVPN-Unsigned.ipa", public / "NEBULA-NativeVPN-StartupFix-Unsigned.ipa")
        shutil.copyfile("dist/release-inventory.json", public / "release-inventory.json")
        (public / "dSYM-inventory.json").write_text(json.dumps(symbols, indent=2) + "\n")
    for path, name in ((ARCHIVE, ARCHIVE.name), (ARCHIVE / "dSYMs", "NEBULA-NativeVPN-dSYMs"),
                       (Path("build/Release-Archive.xcresult"), "Release-Archive.xcresult")):
        if path.is_dir():
            label = "" if success else "INCOMPLETE-"
            with tarfile.open(public / (label + name + ".tar.gz"), "w:gz") as tar:
                tar.add(path, arcname=path.name)
    test_status_path = Path("build-logs/source-tests-exit-status.txt")
    test_status = int(test_status_path.read_text()) if test_status_path.exists() else None
    test_log = Path("build-logs/source-tests.log")
    count = re.findall(r"Ran (\d+) tests?", test_log.read_text() if test_log.exists() else "")
    report = {"commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "provider": "Codemagic", "buildID": os.environ.get("CM_BUILD_ID"),
              "pipelineExitStatus": args.exit_status, "artifactValidationError": evidence_error,
              "unsignedRelease": "PASS" if success else "FAIL", "sourceTestsExitStatus": test_status,
              "sourceTestsRun": int(count[-1]) if count else None,
              "sourceTestScope": "Dependency, package and artifact invariants; not a running iOS app",
              "matchingDSYMs": len(symbols), "developerSigning": "NOT_PERFORMED",
              "appLaunchValidation": "NOT_PERFORMED", "physicalDeviceVPN": "NOT_PERFORMED",
              "signingReadiness": "Two separately matching profiles with the required common Group are still required"}
    (public / "validation-report.json").write_text(json.dumps(report, indent=2) + "\n")
    (public / "test-and-build-report.md").write_text(
        f"# NEBULA unsigned Release\n\nCommit: {report['commit']}\n\n"
        f"Pipeline exit: {args.exit_status}; artifact validation: {evidence_error or 'no additional error'}.\n\n"
        f"Unsigned Release: {report['unsignedRelease']}; matching dSYMs: {len(symbols)}.\n\n"
        f"Source tests: {report['sourceTestsRun']} run, exit {test_status}. See build-logs/source-tests.log.\n\n"
        "Compilation and packaging do not establish error-screen launch or physical-device VPN success. "
        "No signing, device installation or permission grant was performed.\n")
    shutil.copyfile("LICENSE", public / "LICENSE")
    check_public_tree(public)
    files = [p for p in sorted(public.rglob("*")) if p.is_file()]
    (public / "SHA256SUMS.txt").write_text("".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(public).as_posix()}\n" for p in files))
    print(json.dumps(report, indent=2))
    return 1 if evidence_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
