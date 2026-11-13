import SwiftUI

public struct DashboardCardHeader: View {
    private let icon: String
    private let title: LocalizedStringKey

    public init(icon: String, title: LocalizedStringKey) {
        self.icon = icon
        self.title = title
    }

    public var body: some View {
        HStack(spacing: 8) {
            Image(systemName: icon)
                #if os(iOS)
                .foregroundStyle(NebulaTheme.blue)
                #else
                .foregroundStyle(.primary)
                #endif
                .accessibilityHidden(true)
            Text(title)
                .font(.headline)
                .fontWeight(.bold)
        }
    }
}
