import plistlib
import tempfile
import unittest
from pathlib import Path

from preflight import load_json, validate_framework


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.framework = self.root / "Libbox.xcframework"
        self.framework.mkdir()

    def slice(self, identifier="ios-arm64", architectures=None, variant=None):
        bundle = self.framework / identifier / "Libbox.framework"
        (bundle / "Headers").mkdir(parents=True)
        (bundle / "Modules").mkdir()
        (bundle / "Libbox").write_bytes(b"fixture, not an executable")
        (bundle / "Headers/Libbox.h").write_text("// fixture")
        (bundle / "Modules/module.modulemap").write_text("// fixture")
        result = {"LibraryIdentifier": identifier, "LibraryPath": "Libbox.framework", "SupportedPlatform": "ios", "SupportedArchitectures": architectures or ["arm64"]}
        if variant:
            result["SupportedPlatformVariant"] = variant
        return result

    def manifest(self, slices):
        (self.framework / "Info.plist").write_bytes(plistlib.dumps({"AvailableLibraries": slices}))

    def test_missing_dependency_fails(self):
        with self.assertRaisesRegex(ValueError, "Missing Libbox"):
            validate_framework(self.root)

    def test_device_only_is_not_simulator_compatible(self):
        self.manifest([self.slice()])
        self.assertEqual(validate_framework(self.root), "iOS arm64")
        with self.assertRaisesRegex(ValueError, "Simulator"):
            validate_framework(self.root, True, "arm64")

    def test_matching_simulator_slice_is_required(self):
        self.manifest([self.slice(), self.slice("ios-simulator", ["arm64"], "simulator")])
        self.assertIn("Simulator", validate_framework(self.root, True, "arm64"))
        with self.assertRaisesRegex(ValueError, "Simulator"):
            validate_framework(self.root, True, "x86_64")

    def test_missing_binary_is_rejected(self):
        self.manifest([self.slice()])
        (self.framework / "ios-arm64/Libbox.framework/Libbox").unlink()
        with self.assertRaisesRegex(ValueError, "binary"):
            validate_framework(self.root)

    def test_missing_headers_or_module_map_is_rejected(self):
        self.manifest([self.slice()])
        (self.framework / "ios-arm64/Libbox.framework/Headers/Libbox.h").unlink()
        with self.assertRaisesRegex(ValueError, "headers"):
            validate_framework(self.root)

    def test_path_escape_is_rejected(self):
        self.manifest([{"LibraryIdentifier": "../../outside", "LibraryPath": "Libbox.framework", "SupportedPlatform": "ios"}])
        with self.assertRaisesRegex(ValueError, "escapes"):
            validate_framework(self.root)

    def test_duplicate_localization_keys_are_rejected(self):
        path = self.root / "duplicate.json"
        path.write_text('{"same": 1, "same": 2}')
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            load_json(path)


if __name__ == "__main__":
    unittest.main()
