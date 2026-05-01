import AppKit
import SwiftUI

private enum TrainThemeMode: String, CaseIterable {
    case system
    case light
    case dark

    var label: String {
        switch self {
        case .system: "Follow System"
        case .light: "Light"
        case .dark: "Dark"
        }
    }

    var preferredColorScheme: ColorScheme? {
        switch self {
        case .system: nil
        case .light: .light
        case .dark: .dark
        }
    }
}

@main
struct TrainApp: App {
    @StateObject private var viewModel = AppViewModel()
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    @AppStorage("train.theme.mode") private var themeModeRawValue = TrainThemeMode.system.rawValue

    private var themeMode: TrainThemeMode {
        get { TrainThemeMode(rawValue: themeModeRawValue) ?? .system }
        set { themeModeRawValue = newValue.rawValue }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(viewModel)
                .preferredColorScheme(themeMode.preferredColorScheme)
                .onAppear {
                    appDelegate.viewModel = viewModel
                    viewModel.start()
                    viewModel.updateService.checkForUpdates(silent: true)
                }
                .frame(minWidth: 880, minHeight: 640)
        }
        .windowStyle(.hiddenTitleBar)
        .defaultSize(width: 1280, height: 860)
        .commands {
            CommandGroup(replacing: .appInfo) {
                Button("About {train}") {
                    NSApp.orderFrontStandardAboutPanel(nil)
                }
            }
            CommandGroup(after: .appInfo) {
                Button("Check for Updates...") {
                    viewModel.updateService.checkForUpdates(silent: false)
                }
                .keyboardShortcut("u", modifiers: [.command, .shift])

                Divider()

                Button("Start Engine") {
                    viewModel.start()
                }
                .disabled(viewModel.processSupervisor.status == .running || viewModel.processSupervisor.status == .starting)

                Button("Stop Engine") {
                    viewModel.stop()
                }
                .disabled(viewModel.processSupervisor.status == .stopped)
            }

            CommandMenu("Theme") {
                ForEach(TrainThemeMode.allCases, id: \.rawValue) { mode in
                    Button(mode.label) {
                        themeModeRawValue = mode.rawValue
                    }
                    .keyboardShortcut(mode == .light ? "1" : mode == .dark ? "2" : "0", modifiers: [.command, .option])
                }
            }
        }
    }
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    weak var viewModel: AppViewModel?

    func applicationWillTerminate(_ notification: Notification) {
        Task { @MainActor in
            viewModel?.stop()
        }
    }
}
