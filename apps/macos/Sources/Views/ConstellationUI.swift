import SwiftUI

enum ConstellationPalette {
    static let canvas = Color(red: 0.96, green: 0.94, blue: 0.90)
    static let panel = Color.white.opacity(0.86)
    static let panelAlt = Color(red: 0.92, green: 0.88, blue: 0.82)
    static let border = Color(red: 0.84, green: 0.80, blue: 0.73)
    static let textPrimary = Color(red: 0.13, green: 0.11, blue: 0.08)
    static let textSecondary = Color(red: 0.37, green: 0.33, blue: 0.28)
    static let accent = Color(red: 0.72, green: 0.35, blue: 0.17)
    static let success = Color(red: 0.16, green: 0.48, blue: 0.28)
    static let warning = Color(red: 0.66, green: 0.42, blue: 0.0)
    static let danger = Color(red: 0.69, green: 0.23, blue: 0.18)
    static let info = Color(red: 0.17, green: 0.43, blue: 0.63)
}

struct ConstellationShell<Content: View>: View {
    @ViewBuilder var content: Content

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 1.0, green: 0.98, blue: 0.95),
                    ConstellationPalette.canvas
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .overlay(
                RadialGradient(
                    colors: [
                        ConstellationPalette.accent.opacity(0.16),
                        .clear
                    ],
                    center: .topLeading,
                    startRadius: 20,
                    endRadius: 420
                )
            )
            .ignoresSafeArea()

            content
        }
        .tint(ConstellationPalette.accent)
    }
}

struct ConstellationPanelModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(18)
            .background(
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .fill(ConstellationPalette.panel)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .stroke(ConstellationPalette.border.opacity(0.9), lineWidth: 1)
            )
            .shadow(color: Color.black.opacity(0.08), radius: 18, x: 0, y: 12)
    }
}

struct ConstellationInsetModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(8)
            .background(
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .fill(ConstellationPalette.panelAlt.opacity(0.72))
            )
    }
}

extension View {
    func constellationPanel() -> some View {
        modifier(ConstellationPanelModifier())
    }

    func constellationInset() -> some View {
        modifier(ConstellationInsetModifier())
    }
}

struct ConstellationStatusPill: View {
    let text: String
    let color: Color

    var body: some View {
        Text(text.capitalized)
            .font(.caption.weight(.semibold))
            .foregroundStyle(color)
            .padding(.horizontal, 10)
            .padding(.vertical, 4)
            .background(color.opacity(0.12))
            .clipShape(Capsule())
    }
}
