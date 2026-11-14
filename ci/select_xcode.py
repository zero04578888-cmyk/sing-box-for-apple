"""Choose an installed SDK explicitly; fail rather than assume a hosted image is compatible."""
import os
import re
import subprocess
from pathlib import Path

candidates = []
for app in Path("/Applications").glob("Xcode*.app"):
    developer = app / "Contents/Developer"
    env = dict(os.environ, DEVELOPER_DIR=str(developer))
    result = subprocess.run(["xcodebuild", "-version"], env=env, text=True, capture_output=True)
    match = re.search(r"Xcode (\d+)\.(\d+)(?:\.(\d+))?", result.stdout)
    if result.returncode == 0 and match:
        version = tuple(int(part or 0) for part in match.groups())
        if version >= (26, 2, 0):
            candidates.append((version, str(developer)))
if not candidates:
    raise SystemExit("No installed Xcode >= 26.2. Select a compatible macOS runner image; no build was attempted.")
version, developer = sorted(candidates)[0]
subprocess.run(["sudo", "xcode-select", "--switch", developer], check=True)
env_file = os.environ.get("GITHUB_ENV") or os.environ.get("CM_ENV")
if env_file:
    with open(env_file, "a") as output:
        print(f"DEVELOPER_DIR={developer}", file=output)
print(f"Selected Xcode {version}: {developer}")
