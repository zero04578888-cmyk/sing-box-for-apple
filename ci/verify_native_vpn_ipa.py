"""Read back an unsigned IPA and compare it with the validated source .app."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import zipfile

from native_vpn import IDENTITY
from package_unsigned_release import inventory


def verify_ipa(ipa, app):
    bundles = inventory(app, IDENTITY["baseBundleID"], IDENTITY["appGroup"])
    prefix = "Payload/" + app.name + "/"
    expected = {}
    for path in app.rglob("*"):
        if path.is_file() or path.is_symlink():
            data = os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
            expected[prefix + path.relative_to(app).as_posix()] = hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(ipa) as archive:
        members = [item.filename for item in archive.infolist() if not item.is_dir()]
        if len(members) != len(set(members)):
            raise ValueError("Duplicate IPA file entries")
        if set(members) != set(expected):
            raise ValueError("IPA file set differs from the validated App")
        if archive.testzip() is not None:
            raise ValueError("IPA CRC validation failed")
        for name, digest in expected.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                raise ValueError(f"IPA file differs from the validated App: {name}")
        actual = []
        for bundle in bundles:
            path = prefix + ("" if bundle["path"] == "." else bundle["path"] + "/") + "Info.plist"
            info = plistlib.loads(archive.read(path))
            actual.append({"path": path, "bundleID": info["CFBundleIdentifier"],
                           "basePackageIdentifier": info["BasePackageIdentifier"],
                           "appGroup": info["AppGroupIdentifier"]})
    return {"ipaSHA256": hashlib.sha256(ipa.read_bytes()).hexdigest(), "fileCount": len(expected),
            "zipCRC": "PASS", "allFilesMatchValidatedApp": True, "bundles": actual,
            "intendedSigningTeamID": IDENTITY["signingTeamID"], "developerSigning": "NOT_PERFORMED",
            "extensionAuthorization": "NOT_CONFIRMED", "physicalDeviceVPN": "NOT_PERFORMED"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ipa", type=Path, required=True)
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(verify_ipa(args.ipa, args.app), indent=2) + "\n")
