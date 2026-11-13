#!/usr/bin/env bash
set -euo pipefail

# Run from .ci/core. The official core checkout remains unmodified.
test "$(git rev-parse HEAD)" = "$EXPECTED_REVISION"
# ReadTag uses git describe. Fetch the official tag and verify it points at the pinned source.
git fetch --depth=1 origin "refs/tags/$EXPECTED_TAG:refs/tags/$EXPECTED_TAG"
test "$(git rev-parse "$EXPECTED_TAG^{commit}")" = "$EXPECTED_REVISION"
test "$(git describe --tags --exact-match HEAD)" = "$EXPECTED_TAG"
printf 'Verified Libbox version tag: %s\n' "$EXPECTED_TAG"
make lib_install 2>&1 | tee ../../build-logs/libbox-tools.log
export PATH="$(go env GOPATH)/bin:$PATH"
go run ./cmd/internal/build_libbox -target apple -platform "$LIBBOX_PLATFORMS" 2>&1 | tee ../../build-logs/libbox-build.log
git diff --exit-code HEAD
cp -R Libbox.xcframework ../../Libbox.xcframework
