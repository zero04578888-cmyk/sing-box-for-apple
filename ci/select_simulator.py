"""Use an installed iPhone 16 Pro Max, without silently substituting a different device."""
import json
import os
import subprocess

devices = json.loads(subprocess.check_output(["xcrun", "simctl", "list", "devices", "available", "--json"], text=True))["devices"]
matches = [device for runtime, values in devices.items() if "iOS" in runtime for device in values if device["name"] == "iPhone 16 Pro Max"]
if not matches:
    raise SystemExit("No installed iPhone 16 Pro Max Simulator. Install a matching runtime/device before UI validation.")
device = next((item for item in matches if item["state"] == "Booted"), matches[0])
udid = device["udid"]
if device["state"] != "Booted":
    subprocess.run(["xcrun", "simctl", "boot", udid], check=True)
subprocess.run(["xcrun", "simctl", "bootstatus", udid, "-b"], check=True)
subprocess.run(["xcrun", "simctl", "ui", udid, "appearance", "dark"], check=True)
with open(os.environ["GITHUB_ENV"], "a") as output:
    print(f"NEBULA_SIMULATOR_UDID={udid}", file=output)
print(f"Selected iPhone 16 Pro Max: {udid}")
