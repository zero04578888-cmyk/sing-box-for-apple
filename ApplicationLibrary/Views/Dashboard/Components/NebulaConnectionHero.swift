#if os(iOS)
import Library
import NetworkExtension
import SwiftUI

@MainActor
struct NebulaConnectionHero: View {
    @EnvironmentObject private var environments: ExtensionEnvironments
    @EnvironmentObject private var profile: ExtensionProfile
    @Environment(\.sizeCategory) private var sizeCategory

    var body: some View {
        VStack(spacing: 20) {
            header

            StartStopButton(prominent: true)
                .buttonStyle(.plain)
                .accessibilityIdentifier("nebula.connection.toggle")

            VStack(spacing: 8) {
                HStack(spacing: 8) {
                    Circle().fill(statusColor).frame(width: 8, height: 8).accessibilityHidden(true)
                    Text(statusTitle).font(.headline)
                }
                .accessibilityElement(children: .combine)
                .accessibilityIdentifier("nebula.connection.status")
                if profile.status == .connected {
                    RuntimeDurationText(profile: profile)
                        .font(.subheadline.monospacedDigit())
                        .foregroundStyle(.secondary)
                } else if environments.emptyProfiles {
                    Text("Add a profile to get started.")
                        .font(.subheadline).foregroundStyle(.secondary)
                }
            }
            .frame(maxWidth: .infinity)

            Divider()
            Group {
                if sizeCategory.isAccessibilityCategory {
                    VStack(spacing: 12) { navigationLinks }
                } else {
                    HStack(spacing: 12) { navigationLinks }
                }
            }
            .font(.subheadline.weight(.medium))
            .buttonStyle(.plain)
            .foregroundStyle(NebulaTheme.blue)
        }
        .padding(20)
        .modifier(NebulaSurface())
    }

    @ViewBuilder private var header: some View {
        if sizeCategory.isAccessibilityCategory {
            VStack(alignment: .leading, spacing: 8) {
                brandTitle
                previewLabel
            }.frame(maxWidth: .infinity, alignment: .leading)
        } else {
            HStack {
                brandTitle
                Spacer()
                previewLabel
            }
        }
    }

    private var brandTitle: some View {
        Text(verbatim: "NEBULA").font(.title2.weight(.bold)).accessibilityAddTraits(.isHeader)
    }

    @ViewBuilder private var previewLabel: some View {
        if Variant.screenshotMode {
            Text("Preview data").font(.caption).foregroundStyle(.secondary)
        }
    }

    @ViewBuilder private var navigationLinks: some View {
        NavigationLink {
            GroupListView().navigationTitle("Groups")
        } label: {
            Label("Groups", systemImage: "rectangle.3.group")
                .frame(maxWidth: .infinity, minHeight: 44)
        }
        .accessibilityIdentifier("nebula.groups.open")
        NavigationLink {
            ConnectionListView().navigationTitle("Connections")
        } label: {
            Label("Connections", systemImage: "point.3.connected.trianglepath.dotted")
                .frame(maxWidth: .infinity, minHeight: 44)
        }
    }

    private var statusTitle: LocalizedStringKey {
        switch profile.status {
        case .connected: return "Connected"
        case .connecting: return "Connecting…"
        case .disconnecting: return "Disconnecting…"
        case .reasserting: return "Reconnecting…"
        case .disconnected: return "Disconnected"
        case .invalid: return "VPN unavailable"
        @unknown default: return "Unknown"
        }
    }

    private var statusColor: Color {
        switch profile.status {
        case .connected: return NebulaTheme.blue
        case .connecting, .disconnecting, .reasserting: return .orange
        case .invalid: return .red
        default: return .secondary
        }
    }
}

struct NebulaConnectionLabel: View {
    let status: NEVPNStatus
    let busy: Bool
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @ScaledMetric(relativeTo: .largeTitle) private var symbolSize: CGFloat = 40

    var body: some View {
        VStack(spacing: 12) {
            ZStack {
                Circle().fill(NebulaTheme.raisedSurface)
                Circle().strokeBorder(NebulaTheme.gradient, lineWidth: status == .connected ? 3 : 1.5)
                if busy || status == .connecting || status == .disconnecting || status == .reasserting {
                    ProgressView().tint(NebulaTheme.blue)
                } else {
                    Image(systemName: "power")
                        .font(.system(size: min(symbolSize, 64), weight: .medium))
                        .foregroundStyle(NebulaTheme.gradient)
                        .accessibilityHidden(true)
                }
            }
            .frame(width: 144, height: 144)
            Text(status.isConnected ? "Stop" : "Start")
                .font(.headline)
                .foregroundStyle(.primary)
        }
        .padding(8)
        .contentShape(Rectangle())
        .animation(reduceMotion ? nil : .easeOut(duration: 0.2), value: status)
    }
}
#endif
