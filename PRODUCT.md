# Product

<!-- impeccable:product-schema 1 -->

## Platform

ios

## Product Purpose

NEBULA is a visual redesign of the existing sing-box-for-apple iOS client. The primary acceptance device is iPhone 16 Pro Max. Connect, select an outbound, manage profiles and subscriptions, and inspect live service telemetry using the existing sing-box integration.

## Capabilities and Constraints

- Preserve all existing VPN, proxy, subscription, import/export, editor, remote-control, logs, tools, and settings flows.
- Do not change Libbox, protocols, packet-tunnel code, database schemas, or credentials.
- Keep native navigation, Dynamic Type, VoiceOver, safe areas, and Reduce Motion support.
- Verify an unsigned iOS build on a macOS GitHub Actions runner after source changes. Build success is not proof of VPN operation; signing, entitlements, and physical-device validation remain separate gates.
- The repository also targets macOS and tvOS; the NEBULA replacement is scoped to iOS.

## Brand Commitments

The user specified NEBULA: dark navy-black surfaces, blue-violet gradients, refined rounded corners, and restrained motion. App screens are implemented directly in SwiftUI. The user explicitly delegated implementation decisions and requested autonomous execution.

## Evidence on Hand

The existing SFI app, shared ApplicationLibrary views, Library state/services, ExtensionProvider, SFIUITests, and Xcode project. Baseline: 768b3de2baf2461dd06405cba1b2ca4e39da5ea4 on feat/nebula-ui. No baseline simulator screenshots or Libbox.xcframework are present in this checkout. The editing host is Windows without Xcode.

## Open Decisions

Audience beyond existing client users was not specified. No VPN or performance claims may be inferred from the visual redesign.
