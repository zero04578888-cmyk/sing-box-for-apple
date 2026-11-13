import Library
import NetworkExtension
import SwiftUI

@MainActor
public struct StartStopButton: View {
    @EnvironmentObject private var environments: ExtensionEnvironments
    private let showsRuntimeDuration: Bool
    private let prominent: Bool

    public init(showsRuntimeDuration: Bool = false, prominent: Bool = false) {
        self.showsRuntimeDuration = showsRuntimeDuration
        self.prominent = prominent
    }

    public var body: some View {
        Group {
            if let profile = environments.extensionProfile {
                ToggleConnectionButton(showsRuntimeDuration: showsRuntimeDuration, prominent: prominent)
                    .environmentObject(profile)
            } else {
                Button {} label: {
                    #if os(tvOS)
                        Image(systemName: "play.fill")
                    #else
                        Label("Start", systemImage: "play.fill")
                    #endif
                }
                .labelStyle(.iconOnly)
                .disabled(true)
            }
        }
        .disabled(environments.emptyProfiles)
    }

    private struct ToggleConnectionButton: View {
        @EnvironmentObject private var environments: ExtensionEnvironments
        @EnvironmentObject private var profile: ExtensionProfile
        @State private var alert: AlertState?
        @State private var isStarting = false
        @State private var actionInFlight = false
        #if os(iOS)
            @Environment(\.horizontalSizeClass) private var horizontalSizeClass
        #endif
        @Environment(\.accessibilityReduceMotion) private var reduceMotion
        let showsRuntimeDuration: Bool
        let prominent: Bool

        var body: some View {
            Button {
                Task {
                    guard !actionInFlight else { return }
                    actionInFlight = true
                    defer { actionInFlight = false }
                    await switchProfile(!profile.status.isConnected)
                }
            } label: {
                #if os(iOS)
                    if prominent {
                        NebulaConnectionLabel(status: profile.status, busy: actionInFlight)
                    } else {
                        HStack(spacing: 8) {
                            if showsRuntimeDuration {
                                RuntimeDurationText(profile: profile)
                            }

                            if SidebarLayout.isEnabled(horizontalSizeClass) {
                                Image(systemName: profile.status.isConnected ? "stop.fill" : "play.fill")
                            } else if !profile.status.isConnected {
                                Label("Start", systemImage: "play.fill")
                                    .padding(.horizontal, 12)
                            } else {
                                Label("Stop", systemImage: "stop.fill")
                            }
                        }
                        .animation(reduceMotion ? nil : .easeOut(duration: 0.2), value: profile.status.isConnectedStrict)
                    }
                #elseif os(tvOS)
                    if !profile.status.isConnected {
                        Image(systemName: "play.fill")
                    } else {
                        Image(systemName: "stop.fill")
                    }
                #else
                    HStack(spacing: 8) {
                        RuntimeDurationText(profile: profile)

                        if !profile.status.isConnected {
                            Label("Start", systemImage: "play.fill")
                        } else {
                            Label("Stop", systemImage: "stop.fill")
                        }
                    }
                    .animation(.spring(response: 0.35, dampingFraction: 0.75), value: profile.status.isConnectedStrict)
                #endif
            }
            .labelStyle(.iconOnly)
            #if os(iOS)
                .modifier(PrimaryTintModifier())
            #endif
                .disabled(actionInFlight || !profile.status.isEnabled)
                .alert($alert)
                .onChangeCompat(of: profile.status) { status in
                    Task { @MainActor in
                        if isStarting {
                            if status == .disconnected {
                                isStarting = false
                            } else if status.isConnectedStrict {
                                isStarting = false
                                environments.commandClient.connect()
                            }
                        }
                    }
                }
        }

        private nonisolated func switchProfile(_ isEnabled: Bool) async {
            do {
                if isEnabled {
                    await MainActor.run { isStarting = true }
                    try await profile.start()
                } else {
                    try await profile.stop()
                }
            } catch {
                await MainActor.run {
                    isStarting = false
                    let action = isEnabled ? "start service" : "stop service"
                    alert = AlertState(action: action, error: error)
                }
            }
        }
    }
}

#if os(iOS)
    private struct PrimaryTintModifier: ViewModifier {
        func body(content: Content) -> some View {
            if #available(iOS 26.0, *), !Variant.debugNoIOS26 {
                content.tint(.primary)
            } else {
                content
            }
        }
    }
#endif
