# NEBULA iOS dashboard

THESIS: One clear connection action with honest live service telemetry.

OWN-WORLD: Native SwiftUI over dark navy surfaces, the blue-to-violet power stroke, and separate colors for upload and download rates.

STORY: Connect using the existing profile; read its exact Network Extension status; open outbound groups to view and select routes; inspect current rates and service health in Statistics.

FIRST VIEWPORT: Preserve the native iOS navigation shell. Put the NEBULA connection surface first on Dashboard, with the active profile and existing configurable service cards below it. Keep profile management and card configuration available. Statistics gets its own native tab and existing logs, tools, and settings stay reachable.

FORM: Brief-pinned NEBULA; concept seed reference `seed:b2b218e0ad4d9d64` was run, with the explicit user direction taking precedence. The connection control delegates to `StartStopButton` and `ExtensionProfile`; node selection delegates to `GroupListViewModel`; live telemetry comes from `CommandClient`. Keep disconnected history hidden, report service totals as service totals, and do not infer VPN health from a button animation. Support Dynamic Type, safe areas, VoiceOver, increased contrast, and Reduce Motion.

QA: Target iPhone 16 Pro Max. Final tested code cdb1d15ca10c53fc1455364dcd7a5758af9a0aa4 passed run 43380949798: unsigned device build, 11 source tests, and 3 fixture UI tests. Six current-source native captures cover five iPhone 1320×2868 views (dashboard, statistics, groups, dashboard/statistics at Accessibility XXXL), plus iPad Pro 13-inch (M4) default-size dashboard. Independent finish review returned disposition: ship with no material fixes for these six captures. Earlier failed overflow screenshots are superseded, not acceptance evidence. Full iPad flows, landscape, manual VoiceOver/Reduce Motion, signed installation and real VPN verification remain unverified; the phone fixture does not establish them.
