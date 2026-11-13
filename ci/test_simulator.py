"""Test selection constraints with a mocked simctl inventory; these are not device tests."""
import json
import os
import runpy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class SimulatorSelectionTests(unittest.TestCase):
    def execute(self, inventory, device_name="iPhone 16 Pro Max"):
        with tempfile.TemporaryDirectory() as folder:
            environment_file = Path(folder) / "environment"

            def output(command, **kwargs):
                if command == ["xcrun", "simctl", "list", "--json"]:
                    return json.dumps(inventory)
                if command[:3] == ["xcrun", "simctl", "create"]:
                    return "created-device\n"
                self.fail(f"Unexpected command: {command}")

            with patch.dict(os.environ, {"GITHUB_ENV": str(environment_file), "NEBULA_DEVICE_NAME": device_name}), \
                    patch("subprocess.check_output", side_effect=output) as read, \
                    patch("subprocess.run") as run:
                runpy.run_path(str(Path(__file__).with_name("select_simulator.py")), run_name="__main__")
            return environment_file.read_text(), read.call_args_list, run.call_args_list

    def test_old_runtime_cannot_validate_current_test_target(self):
        with self.assertRaisesRegex(SystemExit, "iOS >= 26.2"):
            self.execute({"runtimes": [{"identifier": "iOS-18-6", "version": "18.6", "isAvailable": True}]})

    def test_latest_compatible_runtime_and_exact_device_are_selected(self):
        environment, reads, runs = self.execute({
            "runtimes": [
                {"identifier": "iOS-26-2", "version": "26.2", "isAvailable": True},
                {"identifier": "iOS-26-3", "version": "26.3", "isAvailable": True},
            ],
            "devices": {
                "iOS-26-2": [{"name": "iPhone 16 Pro Max", "udid": "older", "state": "Booted", "isAvailable": True}],
                "iOS-26-3": [
                    {"name": "iPhone 17 Pro Max", "udid": "wrong-device", "state": "Booted", "isAvailable": True},
                    {"name": "iPhone 16 Pro Max", "udid": "target", "state": "Shutdown", "isAvailable": True},
                ],
            },
        })
        self.assertIn("NEBULA_SIMULATOR_UDID=target", environment)
        self.assertEqual(len(reads), 1)
        self.assertEqual(runs[0].args[0], ["xcrun", "simctl", "boot", "target"])

    def test_missing_named_instance_is_created_from_existing_device_type(self):
        environment, reads, runs = self.execute({
            "runtimes": [{"identifier": "iOS-26-2", "version": "26.2", "isAvailable": True}],
            "devices": {},
            "devicetypes": [{"name": "iPhone 16 Pro Max", "identifier": "exact-device-type"}],
        })
        self.assertIn("NEBULA_SIMULATOR_UDID=created-device", environment)
        self.assertEqual(reads[1].args[0], ["xcrun", "simctl", "create", "iPhone 16 Pro Max", "exact-device-type", "iOS-26-2"])

    def test_tablet_capture_selects_requested_type_instead_of_phone(self):
        environment, reads, runs = self.execute({
            "runtimes": [{"identifier": "iOS-26-2", "version": "26.2", "isAvailable": True}],
            "devices": {"iOS-26-2": [{"name": "iPhone 16 Pro Max", "udid": "phone", "state": "Booted", "isAvailable": True}]},
            "devicetypes": [{"name": "iPad Pro 13-inch (M4)", "identifier": "tablet-type"}],
        }, device_name="iPad Pro 13-inch (M4)")
        self.assertIn("NEBULA_SIMULATOR_UDID=created-device", environment)
        self.assertEqual(reads[1].args[0], ["xcrun", "simctl", "create", "iPad Pro 13-inch (M4)", "tablet-type", "iOS-26-2"])


if __name__ == "__main__":
    unittest.main()
