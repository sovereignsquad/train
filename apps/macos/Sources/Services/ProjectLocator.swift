import Foundation

enum ProjectLocator {
    static func resolveRepositoryRoot() -> URL? {
        let env = ProcessInfo.processInfo.environment
        if let override = env["AUTOTRAIN_REPO_ROOT"] {
            let url = URL(fileURLWithPath: override)
            if isRepositoryRoot(url) {
                return url
            }
        }

        let compileTimeSource = URL(fileURLWithPath: #filePath)
        if let candidate = ancestorRepositoryRoot(from: compileTimeSource) {
            return candidate
        }

        let currentDirectory = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
        if let candidate = ancestorRepositoryRoot(from: currentDirectory) {
            return candidate
        }

        let sharedProjects = URL(fileURLWithPath: "/Users/Shared/Projects/autotrain")
        if isRepositoryRoot(sharedProjects) {
            return sharedProjects
        }

        return nil
    }

    private static func ancestorRepositoryRoot(from start: URL) -> URL? {
        var current = start.standardizedFileURL
        if current.hasDirectoryPath == false {
            current.deleteLastPathComponent()
        }

        while current.path != "/" {
            if isRepositoryRoot(current) {
                return current
            }
            current.deleteLastPathComponent()
        }
        return nil
    }

    private static func isRepositoryRoot(_ url: URL) -> Bool {
        let markerPaths = [
            "pyproject.toml",
            "services/api/autotrain_api/main.py",
            "core/autotrain_core",
            "projects/mythology/program.md",
        ]
        return markerPaths.allSatisfy { marker in
            FileManager.default.fileExists(atPath: url.appendingPathComponent(marker).path)
        }
    }

    static func resolveExecutable(named name: String, overrideEnvKey: String? = nil) -> URL? {
        let env = ProcessInfo.processInfo.environment
        if let overrideEnvKey,
           let override = env[overrideEnvKey],
           !override.isEmpty
        {
            let overrideURL = URL(fileURLWithPath: override)
            if FileManager.default.isExecutableFile(atPath: overrideURL.path) {
                return overrideURL
            }
        }

        if let pathValue = env["PATH"] {
            for pathEntry in pathValue.split(separator: ":") {
                let candidate = URL(fileURLWithPath: String(pathEntry)).appendingPathComponent(name)
                if FileManager.default.isExecutableFile(atPath: candidate.path) {
                    return candidate
                }
            }
        }

        let fallbackPaths = [
            "/opt/homebrew/bin/\(name)",
            "/usr/local/bin/\(name)",
            "/usr/bin/\(name)",
            "/bin/\(name)",
        ]

        for fallback in fallbackPaths {
            if FileManager.default.isExecutableFile(atPath: fallback) {
                return URL(fileURLWithPath: fallback)
            }
        }

        return nil
    }
}
