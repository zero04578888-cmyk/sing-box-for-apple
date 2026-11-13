#!/usr/bin/env bash
set -euo pipefail

# Run from .ci/core. The official core checkout remains unmodified.
test "$(git rev-parse HEAD)" = "$EXPECTED_REVISION"
make lib_install 2>&1 | tee ../../build-logs/libbox-tools.log
export PATH="$(go env GOPATH)/bin:$PATH"
go run ./cmd/internal/build_libbox -target apple -platform "$LIBBOX_PLATFORMS" 2>&1 | tee ../../build-logs/libbox-build.log
git diff --exit-code HEAD
cp -R Libbox.xcframework ../../Libbox.xcframework
