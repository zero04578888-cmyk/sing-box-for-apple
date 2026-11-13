# NEBULA source analysis

Baseline: `768b3de2baf2461dd06405cba1b2ca4e39da5ea4` (1.15.0-alpha.13). Local branch: `feat/nebula-ui`. Initial tracked working tree was clean.

## Structure and ownership

| Layer | Owning source | Responsibility |
| --- | --- | --- |
| iOS shell | SFI/Application.swift, MainView.swift | Dependency injection, adaptive TabView/sidebar, sheets, URL imports, background/foreground handling, bottom connection accessory |
| Shared presentation | ApplicationLibrary/Views | Dashboard, profiles, groups, connections, logs, tools, settings; shared with macOS/tvOS |
| Dashboard state | DashboardViewModel, OverviewViewModel, DashboardCardConfiguration | Profile selection, service reload, HTTP proxy preferences, user-configured card ordering/visibility |
| App state | Library/Network/ExtensionEnvironments.swift | Observable service/remote target, shared CommandClient, profile/import notifications and reports |
| Telemetry | Library/Network/CommandClient.swift | Libbox subscriptions, a coalesced traffic snapshot, 30 rate samples per direction, logs, outbound groups, reconnect/suspension handling |
| VPN lifecycle | Library/Network/ExtensionProfile.swift | NEVPNManager loading/installation, status notifications, start/stop/reload/restart |
| Packet tunnel | Extension/PacketTunnelProvider.swift → Library/Network/ExtensionProvider.swift | Network Extension entry point, Libbox setup, platform bridge, tunnel lifecycle |
| Storage | Library/Database | GRDB profiles/preferences, remote servers, subscription updates, import/export |
| Other platforms | MacLibrary, SFM, SFM.System, SFT | macOS app/system-extension variants and tvOS app |
| Auxiliary extensions | Widget, FileProvider, Share, Action, Intents | Existing integrations; remain intact |

## Behavior to preserve

1. UI actions use existing ExtensionProfile and GroupListViewModel operations. Never start a second independent tunnel controller or bypass OS VPN authorization.
2. NEVPNStatus.isConnected includes connecting/disconnecting/reasserting in this codebase. Presentation must use exact status cases before claiming connected; do not reinterpret the shared helper.
3. Status is delivered through CommandClient's traffic snapshot/statusPublisher. Rates and totals are available only when trafficAvailable is true. Historical rates are a rolling buffer, not daily/monthly accounting.
4. The shared command client serves both local and remote control. Keep remote-target navigation and ensure the new statistics screen observes the current CommandClient instance.
5. Profile changes update SharedPreferences and may reload a connected service through OverviewViewModel. Keep the existing ProfileCard and profile-management sheets.
6. Node selection, URL tests, and expand/collapse persistence belong to GroupListViewModel; preserve them.
7. Preserve card customization. Use a single column at accessibility text sizes rather than truncating paired cards.

## Dependency/build findings before changes

- The project uses filesystem-synchronized groups. New files under ApplicationLibrary and SFIUITests are included through existing target membership; no hand-written PBX source entries are needed.
- Shared scheme: SFI; generic iOS destination. The app and several extensions/framework targets form one build graph.
- Libbox.xcframework is referenced at repository root, ignored by Git, and missing. No source-build recipe or compatible kernel revision is pinned in this Apple repository. Choosing an arbitrary released binary could introduce ABI/API incompatibilities.
- Frameworks/Runestone is an initialized submodule at baeb3cbf8332d26b4f7b4c175a01f288ebbf3e7f. Frameworks/TreeSitterJSON5 is a local SPM package depending on it.
- Package.resolved locks 24 remote/transitive Swift packages, including GRDB, QRCode, BinaryCodable, LegacyBinaryCodable, DeviceKit, libghostty-spm, PLCrashReporter, and editor packages. A lockfile is not proof that remote resolution/download currently succeeds.
- Existing sources call iOS 26 APIs behind availability guards; the project was upgraded with Xcode 26.2. Use a sufficiently recent Xcode/SDK rather than assuming old hosted images work.
- System SDK frameworks include NetworkExtension, SwiftUI, WidgetKit, UniformTypeIdentifiers, and platform-specific frameworks. They come from Xcode, not third-party downloads.
- Windows host has Git/GitHub CLI/Python but no swift or xcodebuild. Native compilation, Simulator rendering, and signed VPN tests cannot run here.
- origin is public SagerNet/sing-box-for-apple; the connected account has read access, no upstream push access. A writable fork/target is needed for Actions on these changes.

## Redesign scope

iOS-only tokens and reusable surface/button treatments; a dashboard connection hero reusing StartStopButton; existing profile/card controls retained; clearer selected-node presentation and empty states; real upload/download charts; a statistics tab for live/session telemetry. No synthetic telemetry, new analytics store, kernel edits, protocol edits, or subscription fixtures.
