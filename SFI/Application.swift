import ApplicationLibrary
import Foundation
import Library
import SwiftUI

@main
struct Application: App {
    @UIApplicationDelegateAdaptor private var appDelegate: ApplicationDelegate
    private let startupError: String? = {
        do {
            _ = try FilePath.requireSharedDirectory()
            return nil
        } catch {
            return error.localizedDescription
        }
    }()

    var body: some Scene {
        WindowGroup {
            if let startupError {
                SharedContainerUnavailableView(message: startupError)
            } else {
                ApplicationContent()
            }
        }
    }
}

// Construct shared-storage clients only after the App Group check succeeds.
private struct ApplicationContent: View {
    @StateObject private var environments = ExtensionEnvironments()
    @StateObject private var peerStore = TailscaleSSHPeerStore()
    @StateObject private var tailscaleViewModel = TailscaleStatusViewModel()
    @StateObject private var taildropSendManager = TaildropSendManager()
    @StateObject private var taildropInbox = TaildropInboxViewModel()

    var body: some View {
        MainView()
            .tailscaleStatusSubscription(tailscaleViewModel, environments: environments, peerStore: peerStore)
            .environmentObject(environments)
            .environmentObject(peerStore)
            .environmentObject(tailscaleViewModel)
            .environmentObject(taildropSendManager)
            .environmentObject(taildropInbox)
            .task {
                await ImportedFontStore.shared.bootstrap()
            }
    }
}

private struct SharedContainerUnavailableView: View {
    let message: String

    var body: some View {
        ZStack {
            NebulaTheme.background.ignoresSafeArea()
            ScrollView {
                VStack(spacing: 20) {
                    Image(systemName: "lock.shield")
                        .font(.largeTitle)
                        .foregroundStyle(NebulaTheme.gradient)
                        .accessibilityHidden(true)
                    Text("Shared App Group unavailable")
                        .font(.title2.weight(.semibold))
                        .accessibilityAddTraits(.isHeader)
                    Text(message)
                        .font(.body)
                        .textSelection(.enabled)
                    Text("VPN cannot start until signing authorization is corrected.")
                        .font(.body)
                        .foregroundStyle(.secondary)
                }
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
                .padding(24)
                .frame(maxWidth: 560)
                .background(NebulaTheme.surface, in: RoundedRectangle(cornerRadius: NebulaTheme.radius))
                .padding(24)
                .frame(maxWidth: .infinity)
            }
        }
        .preferredColorScheme(.dark)
        .accessibilityIdentifier("nebula.startup.shared-container-error")
    }
}
