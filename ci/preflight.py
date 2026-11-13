#!/usr/bin/env python3
"""Dependency preflight, deliberately separate from compilation and VPN validation."""
import argparse
import json
import platform
import plistlib
import re
import subprocess
import sys
from pathlib import Path


def load_json(path):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)


def validate_framework(root, require_simulator=False, simulator_arch=None):
    framework = root / "Libbox.xcframework"
    info_path = framework / "Info.plist"
    if not info_path.is_file():
        raise ValueError("Missing Libbox.xcframework/Info.plist; build the pinned official dependency first.")
    with info_path.open("rb") as handle:
        info = plistlib.load(handle)
    device = False
    simulator = False
    for library in info.get("AvailableLibraries", []):
        if library.get("SupportedPlatform") != "ios":
            continue
        identifier = library.get("LibraryIdentifier", "")
        library_path = library.get("LibraryPath", "")
        if not identifier or not library_path:
            raise ValueError("Libbox slice has missing paths.")
        bundle = (framework / identifier / library_path).resolve()
        if not bundle.is_relative_to(framework.resolve()):
            raise ValueError("Libbox slice path escapes the XCFramework.")
        if not (bundle / "Libbox").is_file():
            raise ValueError(f"Missing Libbox binary in {identifier}.")
        if not (bundle / "Modules/module.modulemap").is_file():
            raise ValueError(f"Missing module map in {identifier}.")
        if not list((bundle / "Headers").glob("*.h")):
            raise ValueError(f"Missing public headers in {identifier}.")
        architectures = library.get("SupportedArchitectures", [])
        variant = library.get("SupportedPlatformVariant")
        if not variant and "arm64" in architectures:
            device = True
        if variant == "simulator" and (simulator_arch or platform.machine()) in architectures:
            simulator = True
    if not device:
        raise ValueError("Libbox requires an iOS device arm64 slice.")
    if require_simulator and not simulator:
        raise ValueError("Libbox is missing an iOS Simulator slice for this runner's architecture.")
    return "iOS arm64" + (" + native Simulator" if require_simulator else "")


def validate_sources(root):
    required = [
        "sing-box.xcodeproj/project.pbxproj",
        "sing-box.xcodeproj/xcshareddata/xcschemes/SFI.xcscheme",
        "Frameworks/Runestone/Package.swift",
        "Frameworks/TreeSitterJSON5/Package.swift",
    ]
    for relative in required:
        if not (root / relative).is_file():
            raise ValueError(f"Missing {relative}; initialize recursive submodules.")
    lock = load_json(root / "sing-box.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved")
    pins = lock.get("pins", [])
    if not pins:
        raise ValueError("Package.resolved is empty.")
    for pin in pins:
        if not re.fullmatch(r"[a-f0-9]{40}", pin.get("state", {}).get("revision", "")):
            raise ValueError(f"Unpinned Swift dependency: {pin.get('identity')}")
    catalog = load_json(root / "Localizable.xcstrings")
    if catalog.get("sourceLanguage") != "en":
        raise ValueError("Unexpected localization source language.")
    for path in root.rglob("*.entitlements"):
        if ".ci" in path.parts or "build" in path.parts:
            continue
        with path.open("rb") as handle:
            plistlib.load(handle)
    dependency = load_json(root / "ci/libbox.json")
    if dependency.get("repository") != "SagerNet/sing-box" or not re.fullmatch(r"[a-f0-9]{40}", dependency.get("revision", "")):
        raise ValueError("Libbox must name a fixed official source commit.")
    return len(pins)


def validate_xcode():
    output = subprocess.check_output(["xcodebuild", "-version"], text=True)
    match = re.search(r"Xcode (\d+)\.(\d+)", output)
    if not match or tuple(map(int, match.groups())) < (26, 2):
        raise ValueError("Xcode 26.2 or newer is required by the existing project APIs.")
    return output.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--require-simulator", action="store_true")
    parser.add_argument("--check-xcode", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        count = validate_sources(root)
        print(f"PASS: source metadata, local packages, entitlements, localization; {count} pinned Swift packages.")
        if args.source_only:
            print("NOT CHECKED: downloaded Swift packages, Libbox binary compatibility, compilation, signing, Simulator, VPN.")
            print("Libbox on disk: " + ("present (not validated)" if (root / "Libbox.xcframework").is_dir() else "MISSING"))
        else:
            print("PASS: framework structure: " + validate_framework(root, args.require_simulator))
        if args.check_xcode:
            print(validate_xcode())
    except (ValueError, OSError, KeyError, plistlib.InvalidFileException, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
