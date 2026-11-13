import Libbox
import Library
import SwiftUI

public struct DownloadTrafficCard: View {
    @EnvironmentObject private var commandClient: CommandClient

    public init() {}

    public var body: some View {
        DashboardCardView(title: "") {
            VStack(alignment: .leading, spacing: 8) {
                DashboardCardHeader(icon: "arrow.down.circle.fill", title: "Download")

                if Variant.screenshotMode {
                    Text(verbatim: "249 MB/s")
                        .font(.title2)
                        .fontWeight(.medium)
                    Text("Service total").font(.caption).foregroundStyle(.secondary)
                    Text(verbatim: "5.6 GB")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                } else if commandClient.isConnected, let message = commandClient.status, message.trafficAvailable {
                    Text(verbatim: "\(LibboxFormatBytes(message.downlink))/s")
                        .font(.title2)
                        .fontWeight(.medium)
                    Text("Service total").font(.caption).foregroundStyle(.secondary)
                    Text(LibboxFormatBytes(message.downlinkTotal))
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                } else {
                    Text(verbatim: "...")
                        .font(.title2)
                        .fontWeight(.medium)
                    Text(verbatim: "...")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }

                if Variant.screenshotMode || (commandClient.isConnected && commandClient.status?.trafficAvailable == true) {
                    TrafficLineChart(data: commandClient.downlinkHistory, lineColor: trafficColor)
                } else {
                    Text("Waiting for live data")
                        .font(.caption).foregroundStyle(.secondary)
                        .frame(minHeight: 60)
                }
            }
            .monospacedDigit()
        }
    }

    private var trafficColor: Color {
        #if os(iOS)
            NebulaTheme.blue
        #else
            .primary
        #endif
    }
}
