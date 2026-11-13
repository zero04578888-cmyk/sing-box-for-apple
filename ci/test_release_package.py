"""Native VPN boundaries; fixtures are not signed iOS build evidence."""
import plistlib
from pathlib import Path
import shutil
import tempfile
import unittest

from native_vpn import IDENTITY, validate_identity, validate_sources
from package_unsigned_release import UPSTREAM, check_public_tree, inventory


class NativeVPNPackageTests(unittest.TestCase):
    base = IDENTITY["baseBundleID"]
    group = IDENTITY["appGroup"]

    def make_app(self, folder):
        app = Path(folder) / "sing-box.app"
        for name, suffix in [("sing-box", ""), ("Extension", ".extension")]:
            bundle = app if not suffix else app / "PlugIns/Extension.appex"
            bundle.mkdir(parents=True)
            info = {"CFBundleIdentifier": self.base + suffix, "CFBundleExecutable": name,
                    "CFBundleSupportedPlatforms": ["iPhoneOS"], "BasePackageIdentifier": self.base,
                    "AppGroupIdentifier": self.group, "NebulaNativeVPNOnly": True}
            if not suffix:
                info["BGTaskSchedulerPermittedIdentifiers"] = [self.base + ".update_profiles"]
            else:
                info["NSExtension"] = {"NSExtensionPointIdentifier": "com.apple.networkextension.packet-tunnel"}
            (bundle / "Info.plist").write_bytes(plistlib.dumps(info))
            (bundle / name).write_bytes(b"fixture, not Mach-O")
        return app

    def test_sfi_dependency_graph_and_minimal_capabilities(self):
        report = validate_sources()
        self.assertEqual(report["targets"], ["ApplicationLibrary", "Extension", "Library", "SFI"])
        self.assertEqual(report["requiredProfiles"], 2)
        self.assertEqual(report["extensionProfileStatus"], "MISSING")

    def test_exact_user_identity_and_group_required(self):
        validate_identity(self.base, self.group)
        with self.assertRaisesRegex(ValueError, "exact user-reported"):
            validate_identity(self.base, "group." + self.base)
        with self.assertRaisesRegex(ValueError, "user-specified"):
            validate_identity("com.other.app", self.group)

    def test_exactly_two_components_and_vpn_required(self):
        with tempfile.TemporaryDirectory() as folder:
            app = self.make_app(folder)
            self.assertEqual(len(inventory(app, self.base, self.group)), 2)
            shutil.rmtree(app / "PlugIns/Extension.appex")
            with self.assertRaisesRegex(ValueError, "Incomplete"):
                inventory(app, self.base, self.group)

    def test_auxiliary_extension_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            app = self.make_app(folder)
            extra = app / "PlugIns/WidgetExtension.appex"
            shutil.copytree(app / "PlugIns/Extension.appex", extra)
            info = plistlib.loads((extra/"Info.plist").read_bytes())
            info["CFBundleIdentifier"] = self.base + ".widget"
            (extra/"Info.plist").write_bytes(plistlib.dumps(info))
            with self.assertRaisesRegex(ValueError, "Incomplete/unexpected"):
                inventory(app, self.base, self.group)

    def test_tunnel_group_drift_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            app = self.make_app(folder)
            path = app / "PlugIns/Extension.appex/Info.plist"
            info = plistlib.loads(path.read_bytes())
            info["AppGroupIdentifier"] = "group.not-authorized"
            path.write_bytes(plistlib.dumps(info))
            with self.assertRaisesRegex(ValueError, "Inconsistent runtime"):
                inventory(app, self.base, self.group)

    def test_cloud_metadata_and_missing_variant_marker_are_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            app = self.make_app(folder)
            path = app / "Info.plist"
            info = plistlib.loads(path.read_bytes())
            info["NSUbiquitousContainers"] = {"iCloud." + self.base: {}}
            path.write_bytes(plistlib.dumps(info))
            with self.assertRaisesRegex(ValueError, "not authorized"):
                inventory(app, self.base, self.group)
            info.pop("NSUbiquitousContainers")
            info.pop("NebulaNativeVPNOnly")
            path.write_bytes(plistlib.dumps(info))
            with self.assertRaisesRegex(ValueError, "marker"):
                inventory(app, self.base, self.group)

    def test_upstream_identity_is_refused(self):
        with self.assertRaisesRegex(ValueError, "Upstream identity"):
            inventory(Path("not-needed"), UPSTREAM, self.group)

    def test_profile_and_private_key_never_enter_public_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            profile = root / "embedded.mobileprovision"
            profile.write_bytes(b"fixture")
            with self.assertRaisesRegex(ValueError, "Signing material"):
                check_public_tree(root)
            profile.unlink()
            (root / "unexpected.txt").write_bytes(b"-----BEGIN PRIVATE KEY-----\n" + b"A" * 64 + b"\n-----END PRIVATE KEY-----")
            with self.assertRaisesRegex(ValueError, "Private key block"):
                check_public_tree(root)


if __name__ == "__main__":
    unittest.main()
