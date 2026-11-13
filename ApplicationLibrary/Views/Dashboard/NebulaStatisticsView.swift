#if os(iOS)
import Library
import NetworkExtension
import SwiftUI

@MainActor
public struct NebulaStatisticsView: View {
    @EnvironmentObject private var environments: ExtensionEnvironments
    @Environment(\.scenePhase) private var scenePhase

    public init() {}

    public var body: some View {
        StatisticsContent(commandClient: environments.commandClient)
            .environmentObject(environments)
            .onAppear { environments.connect() }
            .onChangeCompat(of: scenePhase) { phase in
                if phase == .active { environments.connect() }
            }
    }

    private struct StatisticsContent: View {
        @EnvironmentObject private var environments: ExtensionEnvironments
        @Environment(\.sizeCategory) private var sizeCategory
        @ObservedObject var commandClient: CommandClient

        private var live: Bool {
            let targetRunning = environments.remoteServer != nil || environments.extensionProfile?.status == .connected
            return targetRunning && commandClient.isConnected && !commandClient.isReconnecting
        }

        var body: some View {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(environments.remoteServer?.displayName ?? String(localized: "Local Device"))
                            .font(.title2.weight(.bold))
                        Text("Live service statistics")
                            .font(.body).foregroundStyle(.secondary)
                        if Variant.screenshotMode {
                            Text("Preview data").font(.caption).foregroundStyle(.secondary)
                        }
                    }

                    if live {
                        if commandClient.status?.trafficAvailable == true || Variant.screenshotMode {
                            LazyVGrid(columns: columns, spacing: 16) {
                                UploadTrafficCard()
                                DownloadTrafficCard()
                            }
                            Text("Rates show recent samples. Totals are reported by the current service, not daily or monthly usage.")
                                .font(.footnote)
                                .foregroundStyle(.secondary)
                                .fixedSize(horizontal: false, vertical: true)
                        } else {
                            NebulaEmptyState(title: "Traffic unavailable", message: "This service has not reported traffic counters.", systemImage: "chart.xyaxis.line")
                        }

                        Text("Service health").font(.title3.weight(.semibold)).accessibilityAddTraits(.isHeader)
                        LazyVGrid(columns: columns, spacing: 16) {
                            StatusCard()
                            ConnectionsCard()
                        }
                        NavigationLink {
                            ConnectionListView().navigationTitle("Connections")
                        } label: {
                            Label("Connections", systemImage: "list.bullet.rectangle")
                                .frame(maxWidth: .infinity, minHeight: 44, alignment: .leading)
                        }
                    } else {
                        NebulaEmptyState(
                            title: "Waiting for live data",
                            message: "Connect a service to view its current traffic and health. Previous samples are hidden while disconnected.",
                            systemImage: "chart.xyaxis.line"
                        )
                        if let error = commandClient.lastError {
                            Text(error).font(.footnote).foregroundStyle(.secondary).textSelection(.enabled)
                        }
                    }
                }
                .padding(20)
                .frame(maxWidth: 760)
                .frame(maxWidth: .infinity)
                .environmentObject(commandClient)
            }
            .background(NebulaTheme.background)
            .accessibilityIdentifier("nebula.statistics")
        }

        private var columns: [GridItem] {
            Array(repeating: GridItem(.flexible(), spacing: 16, alignment: .top), count: sizeCategory.isAccessibilityCategory ? 1 : 2)
        }
    }
}
#endif
