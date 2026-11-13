# NEBULA iOS dashboard

THESIS: One clear connection action with honest live service telemetry.

OWN-WORLD: Native SwiftUI over dark navy surfaces, the blue-to-violet power stroke, and separate colors for upload and download rates.

STORY: Connect using the existing profile; read its exact Network Extension status; open outbound groups to view and select routes; inspect current rates and service health in Statistics.

FIRST VIEWPORT: Preserve the native iOS navigation shell. Put the NEBULA connection surface first on Dashboard, with the active profile and existing configurable service cards below it. Keep profile management and card configuration available. Statistics gets its own native tab and existing logs, tools, and settings stay reachable.

FORM: Brief-pinned NEBULA; concept seed reference `seed:b2b218e0ad4d9d64` was run, with the explicit user direction taking precedence. The connection control delegates to `StartStopButton` and `ExtensionProfile`; node selection delegates to `GroupListViewModel`; live telemetry comes from `CommandClient`. Keep disconnected history hidden, report service totals as service totals, and do not infer VPN health from a button animation. Support Dynamic Type, safe areas, VoiceOver, increased contrast, and Reduce Motion.

QA: The iPhone 16 Pro Max is the target. Native simulator capture, signed installation, and real VPN verification are pending; an unsigned build alone cannot establish them.
