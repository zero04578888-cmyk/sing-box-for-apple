"""Select the exact device on a runtime supported by the existing SFIUITests target."""
import json
import os
import subprocess

inventory = json.loads(subprocess.check_output(["xcrun", "simctl", "list", "--json"], text=True))
# SFIUITests has IPHONEOS_DEPLOYMENT_TARGET=26.2 in the unchanged project.
runtimes = sorted(
    [runtime for runtime in inventory["runtimes"]
     if runtime.get("isAvailable") and "iOS" in runtime["identifier"]
     and tuple(int(part) for part in runtime["version"].split(".")) >= (26, 2)],
    key=lambda runtime: tuple(int(part) for part in runtime["version"].split(".")),
    reverse=True,
)
if not runtimes:
    raise SystemExit("No available iOS >= 26.2 runtime for the existing SFIUITests target.")
runtime = runtimes[0]
matches = [device for device in inventory["devices"].get(runtime["identifier"], [])
           if device.get("isAvailable") and device["name"] == "iPhone 16 Pro Max"]
if matches:
    device = next((item for item in matches if item["state"] == "Booted"), matches[0])
    udid = device["udid"]
    booted = device["state"] == "Booted"
else:
    device_type = next((item for item in inventory["devicetypes"] if item["name"] == "iPhone 16 Pro Max"), None)
    if not device_type:
        raise SystemExit("The selected Xcode has no iPhone 16 Pro Max device type.")
    udid = subprocess.check_output(["xcrun", "simctl", "create", "iPhone 16 Pro Max", device_type["identifier"], runtime["identifier"]], text=True).strip()
    booted = False
if not booted:
    subprocess.run(["xcrun", "simctl", "boot", udid], check=True)
subprocess.run(["xcrun", "simctl", "bootstatus", udid, "-b"], check=True)
subprocess.run(["xcrun", "simctl", "ui", udid, "appearance", "dark"], check=True)
with open(os.environ["GITHUB_ENV"], "a") as output:
    print(f"NEBULA_SIMULATOR_UDID={udid}", file=output)
print(f"Selected iPhone 16 Pro Max / iOS {runtime['version']}: {udid}")
