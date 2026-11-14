"""Fail closed on symbols from another Release, architecture or component."""
from pathlib import Path
import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import collect_codemagic_release as collector
from collect_codemagic_release import dwarf_path, require_matching_uuids, uuid_pairs

UUID = "17DC9A94-2103-381D-9CDB-435759EBBD9B"


class ReleaseSymbolTests(unittest.TestCase):
    def test_matching_uuid_is_case_insensitive(self):
        require_matching_uuids(f"UUID: {UUID} (arm64) Library", f"UUID: {UUID.lower()} (arm64) Library.dwarf")

    def test_other_build_symbols_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "mismatch"):
            require_matching_uuids(f"UUID: {UUID} (arm64) Library", "UUID: 2BBECCA2-09B5-34D4-A246-AE8DAD516EBE (arm64) Library")

    def test_different_architecture_does_not_match(self):
        with self.assertRaisesRegex(ValueError, "mismatch"):
            require_matching_uuids(f"UUID: {UUID} (arm64) Library", f"UUID: {UUID} (x86_64) Library")

    def test_missing_uuid_is_not_an_empty_match(self):
        with self.assertRaisesRegex(ValueError, "Missing"):
            uuid_pairs("error: no UUID found")

    def test_all_three_component_dwarf_paths_and_path_escape(self):
        archive = Path("archive")
        expected = {"sing-box": "sing-box.app.dSYM", "PlugIns/Extension.appex/Extension": "Extension.appex.dSYM",
                    "Frameworks/Library.framework/Library": "Library.framework.dSYM"}
        for executable, bundle in expected.items():
            self.assertEqual(dwarf_path(archive, executable), archive / "dSYMs" / bundle / "Contents/Resources/DWARF" / Path(executable).name)
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            dwarf_path(archive, "../../outside")

    def run_failed_collection(self, folder):
        previous = Path.cwd()
        try:
            with patch.object(collector, "__file__", str(folder / "ci/collector.py")), \
                 patch("sys.argv", ["collector", "--exit-status", "1"]), \
                 patch.object(collector.subprocess, "check_output", return_value="fixture-commit\n"), \
                 contextlib.redirect_stdout(io.StringIO()):
                return collector.main()
        finally:
            os.chdir(previous)

    def test_failed_pipeline_preserves_logs_but_never_publishes_a_stale_ipa(self):
        previous = Path.cwd()
        try:
            with tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                (folder / "dist").mkdir()
                (folder / "dist/NEBULA-NativeVPN-Unsigned.ipa").write_bytes(b"fixture, not a compiled IPA")
                (folder / "build-logs").mkdir()
                (folder / "build-logs/failure.log").write_text("fixture compiler failure")
                (folder / "LICENSE").write_text("fixture")
                self.assertEqual(self.run_failed_collection(folder), 0)
                public = folder / "codemagic-artifacts"
                self.assertFalse(list(public.glob("*.ipa")))
                self.assertTrue((public / "build-logs/failure.log").is_file())
                report = json.loads((public / "validation-report.json").read_text())
                self.assertEqual(report["unsignedRelease"], "FAIL")
                self.assertEqual(report["appLaunchValidation"], "NOT_PERFORMED")
        finally:
            os.chdir(previous)

    def test_signing_material_blocks_staging_even_on_failure(self):
        previous = Path.cwd()
        try:
            with tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                (folder / "dist").mkdir()
                (folder / "dist/embedded.mobileprovision").write_bytes(b"synthetic fixture")
                with self.assertRaisesRegex(ValueError, "forbidden"):
                    self.run_failed_collection(folder)
                self.assertFalse((folder / "codemagic-artifacts").exists())
        finally:
            os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
