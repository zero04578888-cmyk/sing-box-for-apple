"""Native VPN boundaries; fixtures are not signed iOS build evidence."""
import plistlib
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from native_vpn import IDENTITY, validate_identity, validate_sources
from package_unsigned_release import UPSTREAM, check_public_tree, inventory
from verify_native_vpn_ipa import verify_ipa


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
                for field in ["UTExportedTypeDeclarations", "UTImportedTypeDeclarations"]:
                    info[field] = [{"UTTypeIdentifier": self.base + ".profile"}]
                info["CFBundleDocumentTypes"] = [{"LSItemContentTypes": [self.base + ".profile"]}]
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
        with self.assertRaisesRegex(ValueError, "exact audited"):
            validate_identity(self.base, "group." + self.base)
        with self.assertRaisesRegex(ValueError, "user-specified"):
            validate_identity("com.other.app", self.group)

    def test_retired_team_identity_and_group_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "user-specified"):
            validate_identity("com.Ekg.IYmq", "group.64AF44249V.hE6jb4")
        with self.assertRaisesRegex(ValueError, "exact audited"):
            validate_identity(self.base, "group.64AF44249V.hE6jb4")

    def test_stale_profile_document_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            app = self.make_app(folder)
            path = app / "Info.plist"
            info = plistlib.loads(path.read_bytes())
            info["UTImportedTypeDeclarations"] = [{"UTTypeIdentifier": "com.Ekg.IYmq.profile"}]
            path.write_bytes(plistlib.dumps(info))
            with self.assertRaisesRegex(ValueError, "document type"):
                inventory(app, self.base, self.group)

    def test_hardcoded_runtime_container_template_is_rejected(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            fixture = Path(folder)
            for name in ["sing-box.xcodeproj/project.pbxproj", "SFI/Info.plist", "Extension/Info.plist", "SFI/SFI.entitlements", "Extension/Extension.entitlements"]:
                target = fixture / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / name, target)
            path = fixture / "Extension/Info.plist"
            info = plistlib.loads(path.read_bytes())
            info["AppGroupIdentifier"] = "group.64AF44249V.hE6jb4"
            path.write_bytes(plistlib.dumps(info))
            with self.assertRaisesRegex(ValueError, "Runtime identity"):
                validate_sources(fixture)

    def zip_app(self, app, ipa, stale_group=False, omit_extension=False):
        with zipfile.ZipFile(ipa, "w") as archive:
            for path in app.rglob("*"):
                if not path.is_file() or omit_extension and "PlugIns" in path.parts:
                    continue
                data = path.read_bytes()
                if stale_group and path == app / "Info.plist":
                    info = plistlib.loads(data)
                    info["AppGroupIdentifier"] = "group.64AF44249V.hE6jb4"
                    data = plistlib.dumps(info)
                archive.writestr("Payload/" + app.name + "/" + path.relative_to(app).as_posix(), data)

    def test_actual_ipa_metadata_and_files_are_read_back(self):
        with tempfile.TemporaryDirectory() as folder:
            app = self.make_app(folder)
            ipa = Path(folder) / "fixture.ipa"
            self.zip_app(app, ipa)
            result = verify_ipa(ipa, app)
            self.assertEqual({b["bundleID"] for b in result["bundles"]}, {self.base, self.base + ".extension"})
            self.assertTrue(all(b["appGroup"] == self.group for b in result["bundles"]))

    def test_stale_ipa_metadata_is_rejected_even_with_valid_source_app(self):
        with tempfile.TemporaryDirectory() as folder:
            app = self.make_app(folder)
            ipa = Path(folder) / "fixture.ipa"
            self.zip_app(app, ipa, stale_group=True)
            with self.assertRaisesRegex(ValueError, "differs"):
                verify_ipa(ipa, app)

    def test_ipa_missing_extension_files_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            app = self.make_app(folder)
            ipa = Path(folder) / "fixture.ipa"
            self.zip_app(app, ipa, omit_extension=True)
            with self.assertRaisesRegex(ValueError, "file set"):
                verify_ipa(ipa, app)

    def test_corrupt_ipa_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            app = self.make_app(folder)
            ipa = Path(folder) / "fixture.ipa"
            ipa.write_bytes(b"invalid ZIP fixture")
            with self.assertRaises(zipfile.BadZipFile):
                verify_ipa(ipa, app)

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
