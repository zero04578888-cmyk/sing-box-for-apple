"""Packaging invariants; fixture files are not executable iOS build evidence."""
import plistlib
from pathlib import Path
import tempfile
import unittest

from package_unsigned_release import EXTENSIONS, UPSTREAM, check_public_tree, inventory


class ReleasePackageTests(unittest.TestCase):
    base = "io.example.nebula"
    group = "group.io.example.nebula"

    def make_app(self, root):
        app = Path(root) / "sample.app"
        for name, suffix in [("sample", ""), *EXTENSIONS.items()]:
            bundle = app if not suffix else app / ("Extensions" if name == "IntentsExtension" else "PlugIns") / (name + ".appex")
            bundle.mkdir(parents=True, exist_ok=True)
            info = {"CFBundleIdentifier": self.base + ("." + suffix if suffix else ""),
                    "CFBundleExecutable": name, "CFBundleSupportedPlatforms": ["iPhoneOS"],
                    "BasePackageIdentifier": self.base, "AppGroupIdentifier": self.group}
            if not suffix:
                info.update({"BGTaskSchedulerPermittedIdentifiers": [self.base + ".update_profiles"],
                             "NSUbiquitousContainers": {"iCloud." + self.base: {}}})
            if suffix == "extension":
                info["NSExtension"] = {"NSExtensionPointIdentifier": "com.apple.networkextension.packet-tunnel"}
            (bundle / "Info.plist").write_bytes(plistlib.dumps(info))
            (bundle / name).write_bytes(b"fixture, not Mach-O")
        return app

    def test_all_six_extensions_are_required(self):
        with tempfile.TemporaryDirectory() as directory:
            app = self.make_app(directory)
            self.assertEqual(len(inventory(app, self.base, self.group)), 7)
            (app / "PlugIns/Extension.appex/Info.plist").unlink()
            with self.assertRaises(FileNotFoundError):
                inventory(app, self.base, self.group)

    def test_upstream_identity_is_refused(self):
        with self.assertRaisesRegex(ValueError, "Upstream identity"):
            inventory(Path("not-needed"), UPSTREAM, self.group)

    def test_app_group_drift_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            app = self.make_app(directory)
            path = app / "PlugIns/Extension.appex/Info.plist"
            info = plistlib.loads(path.read_bytes())
            info["AppGroupIdentifier"] = "group.wrong"
            path.write_bytes(plistlib.dumps(info))
            with self.assertRaisesRegex(ValueError, "Inconsistent runtime"):
                inventory(app, self.base, self.group)

    def test_stale_icloud_container_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            app = self.make_app(directory)
            path = app / "Info.plist"
            info = plistlib.loads(path.read_bytes())
            info["NSUbiquitousContainers"] = {"iCloud." + UPSTREAM: {}}
            path.write_bytes(plistlib.dumps(info))
            with self.assertRaisesRegex(ValueError, "iCloud document container"):
                inventory(app, self.base, self.group)

    def test_profile_is_never_public_artifact_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "embedded.mobileprovision").write_bytes(b"fixture")
            with self.assertRaisesRegex(ValueError, "Signing material"):
                check_public_tree(root)

    def test_complete_private_key_block_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Deliberately invalid synthetic bytes; no real signing key is used.
            (root / "unexpected.txt").write_bytes(b"-----BEGIN PRIVATE KEY-----\n" + b"A" * 64 + b"\n-----END PRIVATE KEY-----")
            with self.assertRaisesRegex(ValueError, "Private key block"):
                check_public_tree(root)


if __name__ == "__main__":
    unittest.main()
