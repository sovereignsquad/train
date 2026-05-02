import AppKit
import SwiftUI

enum ConstellationPalette {
    static let chrome = adaptiveColor(light: NSColor(red: 0.99, green: 0.98, blue: 0.95, alpha: 1), dark: NSColor(red: 0.06, green: 0.07, blue: 0.09, alpha: 1))
    static let canvas = adaptiveColor(light: NSColor(red: 0.95, green: 0.94, blue: 0.90, alpha: 1), dark: NSColor(red: 0.08, green: 0.10, blue: 0.12, alpha: 1))
    static let panel = adaptiveColor(light: NSColor.white.withAlphaComponent(0.92), dark: NSColor(red: 0.13, green: 0.15, blue: 0.18, alpha: 0.98))
    static let panelAlt = adaptiveColor(light: NSColor(red: 0.91, green: 0.88, blue: 0.83, alpha: 1), dark: NSColor(red: 0.18, green: 0.20, blue: 0.24, alpha: 1))
    static let border = adaptiveColor(light: NSColor(red: 0.82, green: 0.79, blue: 0.72, alpha: 1), dark: NSColor(red: 0.27, green: 0.31, blue: 0.36, alpha: 1))
    static let textPrimary = adaptiveColor(light: NSColor(red: 0.13, green: 0.11, blue: 0.08, alpha: 1), dark: NSColor(red: 0.95, green: 0.94, blue: 0.91, alpha: 1))
    static let textSecondary = adaptiveColor(light: NSColor(red: 0.35, green: 0.32, blue: 0.28, alpha: 1), dark: NSColor(red: 0.78, green: 0.74, blue: 0.69, alpha: 1))
    static let accent = adaptiveColor(light: NSColor(red: 0.11, green: 0.53, blue: 0.29, alpha: 1), dark: NSColor(red: 0.31, green: 0.77, blue: 0.48, alpha: 1))
    static let success = adaptiveColor(light: NSColor(red: 0.16, green: 0.48, blue: 0.28, alpha: 1), dark: NSColor(red: 0.31, green: 0.77, blue: 0.48, alpha: 1))
    static let warning = adaptiveColor(light: NSColor(red: 0.66, green: 0.42, blue: 0.0, alpha: 1), dark: NSColor(red: 0.88, green: 0.63, blue: 0.20, alpha: 1))
    static let danger = adaptiveColor(light: NSColor(red: 0.69, green: 0.23, blue: 0.18, alpha: 1), dark: NSColor(red: 0.89, green: 0.40, blue: 0.35, alpha: 1))
    static let info = adaptiveColor(light: NSColor(red: 0.17, green: 0.43, blue: 0.63, alpha: 1), dark: NSColor(red: 0.42, green: 0.67, blue: 0.89, alpha: 1))
}

private func adaptiveColor(light: NSColor, dark: NSColor) -> Color {
    Color(
        nsColor: NSColor(name: nil) { appearance in
            appearance.bestMatch(from: [.darkAqua, .aqua]) == .darkAqua ? dark : light
        }
    )
}

struct ConstellationShell<Content: View>: View {
    @ViewBuilder var content: Content

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [
                    ConstellationPalette.chrome,
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
