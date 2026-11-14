# Codemagic: NEBULA native VPN unsigned Release

This workflow builds the startup fix from `fix/nebula-shared-container-startup`
(`fe3621df1eb0cff56b0c6446896929547d691a86`). The CI branch
`ci/nebula-codemagic-unsigned` carries the same Swift sources. It does not change
the existing NEBULA screens, Libbox source, protocols, Bundle IDs or App Group.

## Manual build

1. Connect the existing public fork in Codemagic and select YAML configuration.
2. Select branch `ci/nebula-codemagic-unsigned` and workflow
   `nebula-native-vpn-unsigned` from the root `codemagic.yaml`.
3. Check account minutes/billing before starting. The instance is `mac_mini_m2`,
   with a 90-minute maximum. No automatic triggers are configured.
4. Do not add signing groups, certificates, profiles, P12 passwords, real proxy
   configurations or subscriptions. No App Store Connect integration is needed.
5. Start the build and inspect its actual status and `validation-report.json`.
   A committed configuration is not evidence of a successful cloud build.

## Prerequisites checked on the runner

- Apple silicon macOS, Xcode **26.2 / 17C52**, iPhoneOS SDK **26.2**. The existing
  Xcode selector also supports Codemagic's `CM_ENV` file.
- Recursive submodules, including Runestone at the revision recorded by Git;
  missing, modified or conflicted submodule checkouts fail the gate.
- Existing source preflight and native two-component identity audit; 24 locked
  Swift packages are resolved without updating `Package.resolved`.
- The Go version in `ci/libbox.json` is downloaded from the official Go release
  service for darwin/arm64 and checked against its official SHA-256. The image is
  not assumed to include Go. The selected toolchain version is recorded.
- The unmodified official core revision/tag are verified by the existing
  `ci/build_libbox.sh`. It produces the required iOS arm64 `Libbox.xcframework`;
  headers, module map and slice metadata are checked by `ci/preflight.py`.
- SFI is archived in Release, embedding Packet Tunnel and Library, with developer
  signing disabled and `DEBUG_INFORMATION_FORMAT=dwarf-with-dsym`.

Only dependency caches are retained. No signed IPA, old archive, profile or
Framework cache is reused. A new device Framework is built on the selected host.

## Outputs after a successful build

The existing `ci/package_unsigned_release.py` validates and assembles the Payload
IPA. `ci/collect_codemagic_release.py` checks all three Mach-O files are unsigned
and have exactly matching UUID/architecture dSYMs before publishing the IPA.

- `NEBULA-NativeVPN-StartupFix-Unsigned.ipa`
- `NEBULA-NativeVPN-StartupFix-Unsigned.xcarchive.tar.gz`
- `NEBULA-NativeVPN-dSYMs.tar.gz`
- `Release-Archive.xcresult.tar.gz`
- `release-inventory.json`, `dSYM-inventory.json`, `validation-report.json`
- `test-and-build-report.md`, `build-logs/`, `SHA256SUMS.txt`, `LICENSE`

The full archive preserves App, Packet Tunnel, Frameworks, resources and dSYMs.
This is a manually packaged unsigned IPA, not a signed `-exportArchive` result.
Go function symbols may exist without Go DWARF line information; retained dSYMs
do not imply that every embedded Go address has a source line.

On failure, logs and available archive/result trees are retained with an
`INCOMPLETE-` prefix. A failed attempt never publishes an IPA as a successful
delivery, including if an older IPA happens to exist in `dist`. Only the audited
`codemagic-artifacts` directory is selected for upload; signing material blocks
staging. Abrupt runner termination can prevent the exit collector from running.

## Startup patch review and acceptance boundary

The patch changes four Swift files:

- `Library/Shared/FilePath.swift`: throwing shared-container preflight.
- `SFI/Application.swift`: error screen or deferred construction of the existing
  content, StateObjects and font bootstrap.
- `SFI/ApplicationDelegate.swift`: preflight before crash reporters and services.
- `Library/Network/ExtensionProvider.swift`: independent extension preflight and
  an error from `startTunnel` when shared storage is unavailable.

For the investigated case (identity keys present, shared container unavailable),
static review finds no shared-storage access in the error view. The failing
delegate path returns before crash reporter installation. The extension rejects
startup before accessing sharedDirectory. No private-directory fallback is used.
Missing Info.plist identity keys remain separate configuration failures; the
original `AppConfiguration` fatal checks were not changed speculatively.

The source/package tests cover dependency, artifact, UUID, failure-output and
privacy invariants. They do not launch this iOS UI. A successful archive proves
compilation/linking/packaging, not error-screen behavior on a device. Confirm the
rejection screen and healthy launch separately on a test device after building.

**A launch guard does not grant App Group authorization.** Native VPN still
requires two separately matching profiles for `com.Ekg.IYmq` and
`com.Ekg.IYmq.extension`, both authorizing `group.64AF44249V.hE6jb4` and the
required Network Extension capability. A main profile is not an extension
profile. Preserve the official App and never replace its Bundle ID or container.

## Provider references

- [Codemagic YAML configuration](https://docs.codemagic.io/yaml-basic-configuration/yaml-getting-started/)
- [Xcode 26.2 image specifications](https://docs.codemagic.io/specs-macos/xcode-26-2/)
- [Build machine selection](https://docs.codemagic.io/knowledge-codemagic/machine-type/)
- [Official YAML JSON schema](https://codemagic.io/codemagic-schema.json)
- [Official Go releases](https://go.dev/dl/)
