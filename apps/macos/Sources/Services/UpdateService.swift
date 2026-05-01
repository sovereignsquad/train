import AppKit
import Foundation

enum UpdateCheckError: LocalizedError {
    case noPublishedRelease
    case requestFailed(Int)

    var errorDescription: String? {
        switch self {
        case .noPublishedRelease:
            return "No published release is available yet."
        case .requestFailed(let status):
            return "Update check failed with status \(status)."
        }
    }
}

@MainActor
final class UpdateService: ObservableObject {
    @Published var isChecking = false
    @Published var latestVersion: String?
    @Published var releaseURL: URL?
    @Published var errorMessage: String = ""

    private let releaseEndpoint = URL(string: "https://api.github.com/repos/sovereignsquad/train/releases/latest")!

    func checkForUpdates(silent: Bool = false) {
        guard !isChecking else { return }
        if silent, latestVersion != nil || !errorMessage.isEmpty {
            return
        }
        isChecking = true
        if !silent {
            errorMessage = ""
        }

        Task {
            defer { isChecking = false }
            do {
                var request = URLRequest(url: releaseEndpoint)
                request.timeoutInterval = 10
                request.setValue("application/vnd.github.v3+json", forHTTPHeaderField: "Accept")
                let (data, response) = try await URLSession.shared.data(for: request)
                guard let http = response as? HTTPURLResponse else {
                    throw APIClientError.invalidResponse
                }
                if http.statusCode == 404 {
                    latestVersion = nil
                    releaseURL = nil
                    if !silent {
                        errorMessage = UpdateCheckError.noPublishedRelease.localizedDescription
                    }
                    return
                }
                guard (200...299).contains(http.statusCode) else {
                    throw UpdateCheckError.requestFailed(http.statusCode)
                }
                let release = try JSONDecoder().decode(GitHubRelease.self, from: data)
                latestVersion = release.tagName.replacingOccurrences(of: "v", with: "")
                releaseURL = URL(string: release.htmlURL)
                errorMessage = ""
            } catch {
                if !silent {
                    errorMessage = error.localizedDescription
                }
            }
        }
    }

    func openReleasePage() {
        guard let releaseURL else { return }
        NSWorkspace.shared.open(releaseURL)
    }

    func currentVersion() -> String {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "0.1.0"
    }

    func updateAvailable() -> Bool {
        guard let latestVersion else { return false }
        return compareVersions(currentVersion(), latestVersion) < 0
    }

    private func compareVersions(_ current: String, _ latest: String) -> Int {
        let currentParts = current.split(separator: ".").compactMap { Int(String($0)) }
        let latestParts = latest.split(separator: ".").compactMap { Int(String($0)) }
        let maxCount = max(currentParts.count, latestParts.count)
        for index in 0..<maxCount {
            let lhs = index < currentParts.count ? currentParts[index] : 0
            let rhs = index < latestParts.count ? latestParts[index] : 0
            if lhs < rhs { return -1 }
            if lhs > rhs { return 1 }
        }
        return 0
    }
}
