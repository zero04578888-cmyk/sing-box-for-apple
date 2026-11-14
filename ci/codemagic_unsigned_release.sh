#!/usr/bin/env bash
# No signing credentials, provisioning profiles or real configurations are inputs.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p build-logs dist
finish() {
  local build_status=$?
  trap - EXIT
  set +e
  python3 ci/collect_codemagic_release.py --exit-status "$build_status"
  local evidence_status=$?
  if [[ "$build_status" -ne 0 ]]; then exit "$build_status"; fi
  exit "$evidence_status"
}
trap finish EXIT

[[ "$(uname -s)" == Darwin && "$(uname -m)" == arm64 ]] || {
  echo 'This workflow requires the selected Apple silicon macOS runner.' >&2; exit 1;
}
export LC_ALL=en_US.UTF-8
export DISABLE_SWIFTLINT=1
python3 ci/select_xcode.py | tee build-logs/xcode-selection.log
xcodebuild -version | tee build-logs/xcode.txt
python3 - <<'PY'
import subprocess
assert subprocess.check_output(['xcodebuild', '-version'], text=True).splitlines() == ['Xcode 26.2', 'Build version 17C52'], 'Selected Xcode differs from the verified Release baseline'
PY
xcodebuild -showsdks > build-logs/sdks.txt
[[ "$(xcrun --sdk iphoneos --show-sdk-version)" == 26.2 ]] || { echo 'iPhoneOS SDK 26.2 is required.' >&2; exit 1; }
uname -m > build-logs/runner-architecture.txt
sw_vers > build-logs/macos.txt
git rev-parse HEAD > build-logs/commit.txt
git submodule update --init --recursive 2>&1 | tee build-logs/submodule-update.log
git submodule status --recursive > build-logs/submodules.txt
! grep -Eq '^[-+U]' build-logs/submodules.txt
python3 ci/native_vpn.py > build-logs/native-vpn-source-audit.json
python3 ci/preflight.py --source-only --check-xcode | tee build-logs/source-preflight.txt

# Keep the existing UI/core baseline; ExtensionProvider differs only by the reviewed startup guard.
baseline=69b15b74b21a0f60a4a6d352d9da7e877c6d187f
git cat-file -e "$baseline^{commit}" 2>/dev/null || git fetch --no-tags --depth=1 https://github.com/zero04578888-cmyk/sing-box-for-apple.git "$baseline"
git diff --exit-code "$baseline" -- Library/Network Extension/PacketTunnelProvider.swift ci/libbox.json ci/build_libbox.sh \
  ApplicationLibrary/Views/Dashboard ApplicationLibrary/Views/Groups ApplicationLibrary/Views/Abstract/NebulaTheme.swift \
  ':(exclude)Library/Network/ExtensionProvider.swift'
set +e
python3 -m unittest discover -s ci -p 'test_*.py' -v 2>&1 | tee build-logs/source-tests.log
test_status=${PIPESTATUS[0]}
set -e
echo "$test_status" > build-logs/source-tests-exit-status.txt
[[ "$test_status" -eq 0 ]]

export CORE_REPOSITORY="$(python3 -c 'import json; print(json.load(open("ci/libbox.json"))["repository"])')"
export EXPECTED_REVISION="$(python3 -c 'import json; print(json.load(open("ci/libbox.json"))["revision"])')"
export EXPECTED_TAG="$(python3 -c 'import json; print(json.load(open("ci/libbox.json"))["upstreamTag"])')"
export GOMODCACHE="$PWD/.ci/cache/go-mod"
export GOCACHE="$PWD/.ci/cache/go-build"
export GOFLAGS=-p=4
# The documented Xcode image does not promise Go. Install the exact official toolchain locally.
python3 - <<'PY' | tee build-logs/go-install.log
import hashlib, json, re, tarfile
from pathlib import Path
from urllib.request import urlopen
version = 'go' + json.loads(Path('ci/libbox.json').read_text())['goVersion']
assert re.fullmatch(r'go\d+\.\d+\.\d+', version), 'Invalid pinned Go version'
filename = version + '.darwin-arm64.tar.gz'
releases = json.load(urlopen('https://go.dev/dl/?mode=json&include=all', timeout=60))
release = next(item for item in releases if item['version'] == version)
entry = next(item for item in release['files'] if item['filename'] == filename and item['kind'] == 'archive')
destination = Path('.ci/go-toolchain')
destination.mkdir(parents=True, exist_ok=False)
archive = destination / filename
archive.write_bytes(urlopen('https://go.dev/dl/' + filename, timeout=120).read())
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
assert digest == entry['sha256'], 'Official Go archive SHA-256 mismatch'
with tarfile.open(archive) as tar:
    tar.extractall(destination, filter='data')
print(version, filename, 'SHA256=' + digest)
PY
export PATH="$PWD/.ci/go-toolchain/go/bin:$PATH"
export GOTOOLCHAIN=local
go version | tee build-logs/go-version.txt
python3 - <<'PY'
import json
from pathlib import Path
expected = json.loads(Path('ci/libbox.json').read_text())['goVersion']
assert Path('build-logs/go-version.txt').read_text().split()[2] == 'go' + expected, 'Pinned Go toolchain unavailable'
PY
mkdir -p .ci
git clone --depth=1 --branch "$EXPECTED_TAG" "https://github.com/$CORE_REPOSITORY.git" .ci/core 2>&1 | tee build-logs/core-checkout.log
export LIBBOX_PLATFORMS=ios/arm64
(cd .ci/core && bash ../../ci/build_libbox.sh)
cp ci/libbox.json build-logs/libbox-provenance.json
python3 ci/preflight.py --check-xcode | tee build-logs/framework-preflight.txt

export BASE_PACKAGE_IDENTIFIER="$(python3 -c 'import json; print(json.load(open("ci/native_vpn_identity.json"))["baseBundleID"])')"
export APP_GROUP_IDENTIFIER="$(python3 -c 'import json; print(json.load(open("ci/native_vpn_identity.json"))["appGroup"])')"
packages="$PWD/.ci/cache/SourcePackages"
xcodebuild -resolvePackageDependencies -project sing-box.xcodeproj -scheme SFI \
  -clonedSourcePackagesDirPath "$packages" -onlyUsePackageVersionsFromResolvedFile \
  -skipPackagePluginValidation 2>&1 | tee build-logs/packages.log
git diff --exit-code -- sing-box.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved
args=(-project sing-box.xcodeproj -configuration Release -sdk iphoneos
  -clonedSourcePackagesDirPath "$packages" -disableAutomaticPackageResolution -skipPackagePluginValidation
  "BASE_PACKAGE_IDENTIFIER=$BASE_PACKAGE_IDENTIFIER" "APP_GROUP_IDENTIFIER=$APP_GROUP_IDENTIFIER"
  CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY= DEVELOPMENT_TEAM=
  PROVISIONING_PROFILE_SPECIFIER= PROVISIONING_PROFILE= DEBUG_INFORMATION_FORMAT=dwarf-with-dsym)
xcodebuild -showBuildSettings -json "${args[@]}" -target SFI -target Extension > build-logs/release-build-settings.json
xcodebuild archive "${args[@]}" -scheme SFI -destination 'generic/platform=iOS' \
  -jobs 2 -derivedDataPath build/ReleaseData -archivePath build/NEBULA-NativeVPN-StartupFix-Unsigned.xcarchive \
  -resultBundlePath build/Release-Archive.xcresult 2>&1 | tee build-logs/release-archive.log
python3 ci/package_unsigned_release.py \
  --app build/NEBULA-NativeVPN-StartupFix-Unsigned.xcarchive/Products/Applications/sing-box.app \
  --build-settings build-logs/release-build-settings.json --output dist
