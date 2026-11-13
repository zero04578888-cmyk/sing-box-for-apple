#if os(iOS)
import SwiftUI
import UIKit

/// iOS presentation tokens. Networking and persisted preferences do not depend on this theme.
public enum NebulaTheme {
    public static let background = Color(red: 0.024, green: 0.043, blue: 0.086)
    public static let surface = Color(red: 0.055, green: 0.082, blue: 0.145)
    public static let raisedSurface = Color(red: 0.086, green: 0.118, blue: 0.196)
    public static let blue = Color(red: 0.49, green: 0.70, blue: 1.0)
    public static let violet = Color(red: 0.72, green: 0.63, blue: 1.0)
    public static let border = Color(uiColor: UIColor { traits in
        UIColor(white: 1, alpha: traits.accessibilityContrast == .high ? 0.45 : 0.14)
    })
    public static let gradient = LinearGradient(colors: [blue, violet], startPoint: .topLeading, endPoint: .bottomTrailing)
    public static let radius: CGFloat = 16
    public static let spacing: CGFloat = 16
}

struct NebulaSurface: ViewModifier {
    func body(content: Content) -> some View {
        content
            .background(NebulaTheme.surface, in: RoundedRectangle(cornerRadius: NebulaTheme.radius, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: NebulaTheme.radius, style: .continuous)
                    .strokeBorder(NebulaTheme.border, lineWidth: 1)
                    .allowsHitTesting(false)
            }
    }
}

struct NebulaEmptyState: View {
    let title: LocalizedStringKey
    let message: LocalizedStringKey
    let systemImage: String

    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: systemImage)
                .font(.largeTitle)
                .foregroundStyle(NebulaTheme.blue)
                .accessibilityHidden(true)
            Text(title)
                .font(.title3.weight(.semibold))
                .accessibilityAddTraits(.isHeader)
            Text(message)
                .font(.body)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(24)
        .frame(maxWidth: .infinity)
    }
}
#endif
