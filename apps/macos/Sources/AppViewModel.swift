import Foundation

@MainActor
final class AppViewModel: ObservableObject {
    @Published var health: HealthPayload?
    @Published var projects: [ProjectPayload] = []
    @Published var runs: [RunPayload] = []
    @Published var projectStates: [ProjectStatePayload] = []
    @Published var providers: [ProviderPayload] = []
    @Published var agentStatus: AgentStatusPayload?
    @Published var operatorStatus: OperatorStatusPayload?
    @Published var lastRefreshError: String = ""

    let processSupervisor = ProcessSupervisorService()
    let updateService = UpdateService()

    private var refreshTask: Task<Void, Never>?

    func start() {
        processSupervisor.startEngine()
        beginRefreshing()
    }

    func stop() {
        refreshTask?.cancel()
        refreshTask = nil
        processSupervisor.stopEngine()
    }

    func refreshNow() {
        Task { await refreshSnapshot() }
    }

    func resumeRun(_ runID: Int) {
        Task {
            guard let client = apiClient() else { return }
            do {
                _ = try await client.post("v1/runs/\(runID)/resume", as: RunPayload.self)
                await refreshSnapshot()
            } catch {
                lastRefreshError = error.localizedDescription
            }
        }
    }

    func createProject(_ payload: ProjectWritePayload) {
        Task {
            guard let client = apiClient() else { return }
            do {
                _ = try await client.post("v1/projects", body: payload, as: ProjectPayload.self)
                await refreshSnapshot()
            } catch {
                lastRefreshError = error.localizedDescription
            }
        }
    }

    func updateProject(_ key: String, payload: ProjectWritePayload) {
        Task {
            guard let client = apiClient() else { return }
            do {
                _ = try await client.put("v1/projects/\(key)", body: payload, as: ProjectPayload.self)
                await refreshSnapshot()
            } catch {
                lastRefreshError = error.localizedDescription
            }
        }
    }

    func deleteProject(_ key: String) {
        Task {
            guard let client = apiClient() else { return }
            do {
                try await client.delete("v1/projects/\(key)")
                await refreshSnapshot()
            } catch {
                lastRefreshError = error.localizedDescription
            }
        }
    }

    func bootstrapProject(_ key: String, overwrite: Bool = false) {
        Task {
            guard let client = apiClient() else { return }
            do {
                let payload = ProjectBootstrapRequestPayload(overwrite: overwrite)
                _ = try await client.post(
                    "v1/projects/\(key)/bootstrap",
                    body: payload,
                    as: ProjectBootstrapPayload.self
                )
                await refreshSnapshot()
            } catch {
                lastRefreshError = error.localizedDescription
            }
        }
    }

    private func beginRefreshing() {
        refreshTask?.cancel()
        refreshTask = Task { [weak self] in
            guard let self else { return }
            while !Task.isCancelled {
                await refreshSnapshot()
                try? await Task.sleep(for: .seconds(5))
            }
        }
    }

    private func refreshSnapshot() async {
        guard let client = apiClient() else { return }

        do {
            async let health: HealthPayload = client.get("health", as: HealthPayload.self)
            async let projects: [ProjectPayload] = client.get("v1/projects", as: [ProjectPayload].self)
            async let runs: [RunPayload] = client.get("v1/runs", as: [RunPayload].self)
            async let states: [ProjectStatePayload] = client.get("v1/project-states", as: [ProjectStatePayload].self)
            async let providers: [ProviderPayload] = fetchProviders(using: client)
            async let agent: AgentStatusPayload = client.get("v1/agents/mistral-vibe", as: AgentStatusPayload.self)
            async let operatorSnapshot: OperatorStatusPayload = client.get("v1/operator/status", as: OperatorStatusPayload.self)

            self.health = try await health
            self.projects = try await projects
            self.runs = try await runs
            self.projectStates = try await states
            self.providers = try await providers
            self.agentStatus = try await agent
            self.operatorStatus = try await operatorSnapshot
            self.lastRefreshError = ""
        } catch {
            lastRefreshError = error.localizedDescription
        }
    }

    private func fetchProviders(using client: APIClient) async throws -> [ProviderPayload] {
        let adapterList = try await client.get("v1/providers", as: [ProviderAdapterListPayload].self)
        var results: [ProviderPayload] = []
        for adapter in adapterList {
            results.append(try await client.get("v1/providers/\(adapter.key)", as: ProviderPayload.self))
        }
        return results
    }

    private func apiClient() -> APIClient? {
        guard let baseURL = processSupervisor.apiBaseURL else {
            lastRefreshError = "Engine base URL is unavailable."
            return nil
        }
        return APIClient(baseURL: baseURL)
    }
}

private struct ProviderAdapterListPayload: Codable {
    let key: String
}
