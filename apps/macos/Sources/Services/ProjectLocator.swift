import Foundation

enum ProjectLocator {
    static func applicationSupportRoot() -> URL {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        return base.appendingPathComponent("train", isDirectory: true)
    }

    static func resolveRepositoryRoot() -> URL? {
        let env = ProcessInfo.processInfo.environment
        if let override = env["TRAIN_REPO_ROOT"] {
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

        let sharedProjects = URL(fileURLWithPath: "/Users/Shared/Projects/train")
        if isRepositoryRoot(sharedProjects) {
            return sharedProjects
        }

        return bootstrapBundledRuntime()
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
            "services/api/train_api/main.py",
            "core/train_core",
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

    private static func bootstrapBundledRuntime() -> URL? {
        guard let resourceRoot = Bundle.main.resourceURL else {
            return nil
        }

        let bundledRuntime = resourceRoot.appendingPathComponent("runtime-template", isDirectory: true)
        guard isRepositoryRoot(bundledRuntime) else {
            return nil
        }

        let runtimeRoot = applicationSupportRoot()
            .appendingPathComponent("runtime", isDirectory: true)
            .appendingPathComponent("current", isDirectory: true)

        if isRepositoryRoot(runtimeRoot) {
            return runtimeRoot
        }

        do {
            let parent = runtimeRoot.deletingLastPathComponent()
            try FileManager.default.createDirectory(at: parent, withIntermediateDirectories: true)
            if FileManager.default.fileExists(atPath: runtimeRoot.path) {
                try FileManager.default.removeItem(at: runtimeRoot)
            }
            try FileManager.default.copyItem(at: bundledRuntime, to: runtimeRoot)
            return runtimeRoot
        } catch {
            return nil
        }
    }
}
