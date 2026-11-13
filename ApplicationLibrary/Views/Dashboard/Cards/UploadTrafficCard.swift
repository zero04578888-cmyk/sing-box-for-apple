import Libbox
import Library
import SwiftUI

public struct UploadTrafficCard: View {
    @EnvironmentObject private var commandClient: CommandClient

    public init() {}

    public var body: some View {
        DashboardCardView(title: "") {
            VStack(alignment: .leading, spacing: 8) {
                DashboardCardHeader(icon: "arrow.up.circle.fill", title: "Upload")

                if Variant.screenshotMode {
                    Text(verbatim: "38 B/s")
                        .font(.title2)
                        .fontWeight(.medium)
                    Text("Service total").font(.caption).foregroundStyle(.secondary)
                    Text(verbatim: "52 MB")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                } else if commandClient.isConnected, let message = commandClient.status, message.trafficAvailable {
                    Text(verbatim: "\(LibboxFormatBytes(message.uplink))/s")
                        .font(.title2)
                        .fontWeight(.medium)
                    Text("Service total").font(.caption).foregroundStyle(.secondary)
                    Text(LibboxFormatBytes(message.uplinkTotal))
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
                    TrafficLineChart(data: commandClient.uplinkHistory, lineColor: trafficColor)
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
            NebulaTheme.violet
        #else
            .primary
        #endif
    }
}
