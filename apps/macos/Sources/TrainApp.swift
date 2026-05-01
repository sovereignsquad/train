import AppKit
import SwiftUI

@main
struct TrainApp: App {
    @StateObject private var viewModel = AppViewModel()
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(viewModel)
                .onAppear {
                    appDelegate.viewModel = viewModel
                    viewModel.start()
                    viewModel.updateService.checkForUpdates()
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
                    viewModel.updateService.checkForUpdates()
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
