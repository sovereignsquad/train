import Darwin
import Foundation

enum EngineStatus: String {
    case stopped
    case starting
    case running
    case failed
}

@MainActor
final class ProcessSupervisorService: ObservableObject {
    @Published var status: EngineStatus = .stopped
    @Published var statusMessage: String = "Engine is stopped."
    @Published var logs: [String] = []
    @Published var apiBaseURL: URL?
    @Published var repositoryRoot: URL?
    @Published var databaseURL: String = ""
    @Published var uvExecutablePath: String = ""
    @Published var activePort: Int = 8420

    private let host = "127.0.0.1"
    private let preferredPort = 8420
    private var process: Process?
    private var outputPipe: Pipe?
    private var logFileHandle: FileHandle?
    private var healthTask: Task<Void, Never>?
    private var adoptedExternalEngine = false
    private var consecutiveHealthFailures = 0

    init() {
        repositoryRoot = ProjectLocator.resolveRepositoryRoot()
        apiBaseURL = URL(string: "http://\(host):\(preferredPort)")
        activePort = preferredPort
        databaseURL = "sqlite:///\(appSupportDirectory().appendingPathComponent("state/train.db").path)"
    }

    func startEngine() {
        guard process == nil, adoptedExternalEngine == false else {
            statusMessage = adoptedExternalEngine ? "Already attached to an existing engine." : "Engine is already running."
            return
        }
        status = .starting
        statusMessage = "Preparing engine launch..."
        Task { await startEngineWorkflow() }
    }

    private func startEngineWorkflow() async {
        guard let repositoryRoot else {
            status = .failed
            statusMessage = "Runtime root could not be resolved."
            appendLog("Runtime root missing. Set TRAIN_REPO_ROOT for development or ensure the app bundle includes a runtime template.")
            return
        }
        guard let uvExecutable = ProjectLocator.resolveExecutable(
            named: "uv",
            overrideEnvKey: "TRAIN_UV_EXECUTABLE"
        ) else {
            status = .failed
            statusMessage = "The uv executable could not be resolved."
            appendLog("uv executable missing. Install uv or set TRAIN_UV_EXECUTABLE to an absolute executable path.")
            return
        }
        uvExecutablePath = uvExecutable.path

        let stateDirectory = appSupportDirectory()
        let logsDirectory = stateDirectory.appendingPathComponent("logs", isDirectory: true)
        let runtimeDirectory = stateDirectory.appendingPathComponent("runtime", isDirectory: true)
        let stateFilesDirectory = stateDirectory.appendingPathComponent("state", isDirectory: true)
        let logFileURL = logsDirectory.appendingPathComponent("engine.log")
        databaseURL = "sqlite:///\(stateFilesDirectory.appendingPathComponent("train.db").path)"

        do {
            try FileManager.default.createDirectory(at: stateDirectory, withIntermediateDirectories: true)
            try FileManager.default.createDirectory(at: logsDirectory, withIntermediateDirectories: true)
            try FileManager.default.createDirectory(at: runtimeDirectory, withIntermediateDirectories: true)
            try FileManager.default.createDirectory(at: stateFilesDirectory, withIntermediateDirectories: true)
            FileManager.default.createFile(atPath: logFileURL.path, contents: nil)
            logFileHandle = try FileHandle(forWritingTo: logFileURL)
            try logFileHandle?.seekToEnd()
        } catch {
            status = .failed
            statusMessage = "Failed to prepare app support directories."
            appendLog("Directory preparation failed: \(error.localizedDescription)")
            return
        }

        do {
            try ensureManagedRuntime(at: repositoryRoot, using: uvExecutable)
        } catch {
            status = .failed
            statusMessage = "Failed to prepare the managed runtime."
            appendLog("Managed runtime bootstrap failed: \(error.localizedDescription)")
            try? logFileHandle?.close()
            logFileHandle = nil
            return
        }

        let preferredBaseURL = baseURL(for: preferredPort)
        if await isHealthyEngine(at: preferredBaseURL) {
            adoptedExternalEngine = true
            activePort = preferredPort
            apiBaseURL = preferredBaseURL
            status = .running
            statusMessage = "Attached to existing engine on port \(preferredPort)."
            consecutiveHealthFailures = 0
            appendLog("Attached to existing healthy engine at \(preferredBaseURL.absoluteString)")
            startHealthPolling()
            return
        }

        guard let selectedPort = firstAvailablePort(startingAt: preferredPort, attempts: 20) else {
            status = .failed
            statusMessage = "No free local port was available for the engine."
            appendLog("Port allocation failed. Tried ports \(preferredPort)-\(preferredPort + 19).")
            return
        }
        activePort = selectedPort
        apiBaseURL = baseURL(for: selectedPort)

        let pipe = Pipe()
        let fileHandle = logFileHandle
        let process = Process()
        process.currentDirectoryURL = repositoryRoot
        process.executableURL = uvExecutable
        process.arguments = [
            "run",
            "uvicorn",
            "train_api.main:app",
            "--host",
            host,
            "--port",
            String(selectedPort),
        ]
        var env = ProcessInfo.processInfo.environment
        env["TRAIN_BUNDLED_APP"] = ProjectLocator.bundledAppModeEnabled() ? "1" : "0"
        env["TRAIN_ENV"] = "local"
        env["APP_HOST"] = host
        env["APP_PORT"] = String(selectedPort)
        env["DATABASE_URL"] = databaseURL
        env["TRAIN_ROOT_DIR"] = repositoryRoot.path
        env["TRAIN_STATE_DIR"] = stateFilesDirectory.path
        env["MISTRAL_VIBE_HOME"] = runtimeDirectory.appendingPathComponent("vibe-home").path
        env["PYTHONUNBUFFERED"] = "1"
        process.environment = env
        process.standardOutput = pipe
        process.standardError = pipe
        process.terminationHandler = { [weak self] task in
            Task { @MainActor in
                self?.appendLog("Engine terminated with status \(task.terminationStatus).")
                self?.process = nil
                self?.outputPipe = nil
                self?.adoptedExternalEngine = false
                self?.healthTask?.cancel()
                self?.healthTask = nil
                self?.consecutiveHealthFailures = 0
                self?.status = task.terminationStatus == 0 ? .stopped : .failed
                self?.statusMessage = task.terminationStatus == 0
                    ? "Engine stopped."
                    : "Engine failed with exit code \(task.terminationStatus)."
                try? self?.logFileHandle?.close()
                self?.logFileHandle = nil
            }
        }

        pipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            if data.isEmpty { return }
            if let text = String(data: data, encoding: .utf8) {
                Task { @MainActor in
                    self?.appendLog(text.trimmingCharacters(in: .newlines))
                }
                try? fileHandle?.write(contentsOf: data)
            }
        }

        do {
            try process.run()
            self.process = process
            self.outputPipe = pipe
            self.adoptedExternalEngine = false
            self.consecutiveHealthFailures = 0
            self.status = .starting
            self.statusMessage = "Starting local engine on port \(selectedPort)..."
            appendLog("Launching engine from \(repositoryRoot.path)")
            appendLog("Using uv at \(uvExecutable.path)")
            if selectedPort != preferredPort {
                appendLog("Preferred port \(preferredPort) was unavailable. Using port \(selectedPort).")
            }
            startHealthPolling()
        } catch {
            status = .failed
            statusMessage = "Failed to start the engine."
            appendLog("Engine launch failed: \(error.localizedDescription)")
            try? logFileHandle?.close()
            logFileHandle = nil
        }
    }

    func stopEngine() {
        healthTask?.cancel()
        healthTask = nil
        if adoptedExternalEngine {
            adoptedExternalEngine = false
            consecutiveHealthFailures = 0
            status = .stopped
            statusMessage = "Detached from existing engine."
            appendLog("Detached from existing engine at \(apiBaseURL?.absoluteString ?? "unknown").")
        } else {
            outputPipe?.fileHandleForReading.readabilityHandler = nil
            process?.terminate()
            process = nil
            outputPipe = nil
            consecutiveHealthFailures = 0
            status = .stopped
            statusMessage = "Engine stopped."
            appendLog("Stop requested.")
        }
        try? logFileHandle?.close()
        logFileHandle = nil
    }

    private func startHealthPolling() {
        healthTask?.cancel()
        healthTask = Task { [weak self] in
            guard let self else { return }
            guard let apiBaseURL else { return }
            let client = APIClient(baseURL: apiBaseURL)

            while !Task.isCancelled {
                do {
                    let health = try await client.get("health", as: HealthPayload.self)
                    consecutiveHealthFailures = 0
                    status = .running
                    statusMessage = "\(health.service) is healthy in \(health.environment) on port \(activePort)."
                } catch {
                    if status == .starting {
                        statusMessage = "Waiting for the engine health endpoint..."
                    } else if process != nil || adoptedExternalEngine {
                        consecutiveHealthFailures += 1
                        let message = APIClient.message(for: error)
                        if consecutiveHealthFailures < 3 {
                            statusMessage = "Retrying health check: \(message)"
                        } else {
                            status = .failed
                            statusMessage = "Health check failed: \(message)"
                        }
                    }
                }
                try? await Task.sleep(for: .seconds(2))
            }
        }
    }

    private func appSupportDirectory() -> URL {
        ProjectLocator.applicationSupportRoot()
    }

    private func appendLog(_ line: String) {
        guard !line.isEmpty else { return }
        logs.append("[\(timestamp())] \(line)")
        if logs.count > 2000 {
            logs.removeFirst(logs.count - 1000)
        }
    }

    private func timestamp() -> String {
        ISO8601DateFormatter().string(from: Date())
    }

    private func baseURL(for port: Int) -> URL {
        URL(string: "http://\(host):\(port)")!
    }

    private func ensureManagedRuntime(at repositoryRoot: URL, using uvExecutable: URL) throws {
        let venvPath = repositoryRoot.appendingPathComponent(".venv").path
        let lockPath = repositoryRoot.appendingPathComponent("uv.lock").path

        if FileManager.default.fileExists(atPath: venvPath),
           FileManager.default.fileExists(atPath: lockPath) {
            return
        }

        appendLog("Bootstrapping managed runtime in \(repositoryRoot.path)")

        let syncProcess = Process()
        let pipe = Pipe()
        syncProcess.currentDirectoryURL = repositoryRoot
        syncProcess.executableURL = uvExecutable
        syncProcess.arguments = ["sync", "--frozen", "--no-dev"]
        syncProcess.standardOutput = pipe
        syncProcess.standardError = pipe

        try syncProcess.run()
        syncProcess.waitUntilExit()

        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        if let output = String(data: data, encoding: .utf8), output.isEmpty == false {
            for line in output.split(separator: "\n", omittingEmptySubsequences: true) {
                appendLog(String(line))
            }
        }

        if syncProcess.terminationStatus != 0 {
            throw NSError(
                domain: "ProcessSupervisorService",
                code: Int(syncProcess.terminationStatus),
                userInfo: [NSLocalizedDescriptionKey: "uv sync failed with exit code \(syncProcess.terminationStatus)"]
            )
        }
    }

    private func isHealthyEngine(at baseURL: URL) async -> Bool {
        do {
            let health = try await APIClient(baseURL: baseURL).get("health", as: HealthPayload.self)
            return health.service == "train-api" && health.status == "ok"
        } catch {
            return false
        }
    }

    private func firstAvailablePort(startingAt startPort: Int, attempts: Int) -> Int? {
        for port in startPort..<(startPort + attempts) {
            if isPortAvailable(port) {
                return port
            }
        }
        return nil
    }

    private func isPortAvailable(_ port: Int) -> Bool {
        let socketDescriptor = socket(AF_INET, SOCK_STREAM, 0)
        guard socketDescriptor >= 0 else {
            return false
        }
        defer { close(socketDescriptor) }

        var value: Int32 = 1
        setsockopt(socketDescriptor, SOL_SOCKET, SO_REUSEADDR, &value, socklen_t(MemoryLayout<Int32>.size))

        var address = sockaddr_in()
        address.sin_len = UInt8(MemoryLayout<sockaddr_in>.size)
        address.sin_family = sa_family_t(AF_INET)
        address.sin_port = in_port_t(UInt16(port).bigEndian)
        address.sin_addr = in_addr(s_addr: inet_addr(host))

        let result = withUnsafePointer(to: &address) { pointer -> Int32 in
            pointer.withMemoryRebound(to: sockaddr.self, capacity: 1) { sockaddrPointer in
                bind(socketDescriptor, sockaddrPointer, socklen_t(MemoryLayout<sockaddr_in>.size))
            }
        }
        return result == 0
    }
}
