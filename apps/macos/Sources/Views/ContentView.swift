import SwiftUI

private enum SidebarPage: String, CaseIterable, Identifiable {
    case overview
    case runs
    case recovery
    case projects
    case logs

    var id: String { rawValue }

    var title: String {
        switch self {
        case .overview: "Overview"
        case .runs: "Runs"
        case .recovery: "Recovery"
        case .projects: "Projects"
        case .logs: "Logs"
        }
    }

    var icon: String {
        switch self {
        case .overview: "gauge.with.dots.needle.50percent"
        case .runs: "play.square.stack"
        case .recovery: "arrow.clockwise.heart"
        case .projects: "square.grid.2x2"
        case .logs: "doc.text.magnifyingglass"
        }
    }
}

struct ContentView: View {
    @EnvironmentObject private var viewModel: AppViewModel
    @State private var selectedPage: SidebarPage? = .overview

    var body: some View {
        NavigationSplitView {
            List(SidebarPage.allCases, selection: $selectedPage) { page in
                Label(page.title, systemImage: page.icon)
                    .tag(page)
            }
            .navigationSplitViewColumnWidth(min: 160, ideal: 200)
        } detail: {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    header
                    engineCard
                    if !viewModel.lastRefreshError.isEmpty {
                        errorBanner(viewModel.lastRefreshError)
                    }
                    detailContent
                }
                .padding(24)
            }
            .frame(minWidth: 760, minHeight: 620)
        }
        .toolbar {
            ToolbarItemGroup(placement: .primaryAction) {
                Button("Refresh") {
                    viewModel.refreshNow()
                }
                Button("Check Updates") {
                    viewModel.updateService.checkForUpdates()
                }
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

    @ViewBuilder
    private var detailContent: some View {
        switch selectedPage ?? .overview {
        case .overview:
            overviewGrid
        case .runs:
            runsSection
        case .recovery:
            recoverySection
        case .projects:
            ProjectManagementView()
        case .logs:
            logsSection
        }
    }

    private var header: some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 6) {
                Text("{train}")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                Text("Native operator shell for the local experiment engine.")
                    .foregroundStyle(.secondary)
                if let repositoryRoot = viewModel.processSupervisor.repositoryRoot {
                    Text(repositoryRoot.path)
                        .font(.caption)
                        .foregroundStyle(.tertiary)
                        .textSelection(.enabled)
                }
            }
            Spacer()
        }
    }

    private var engineCard: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 10) {
                statusRow("Engine Status", viewModel.processSupervisor.status.rawValue.capitalized)
                statusRow("Engine Message", viewModel.processSupervisor.statusMessage)
                statusRow("API URL", viewModel.processSupervisor.apiBaseURL?.absoluteString ?? "n/a")
                statusRow("Active Port", "\(viewModel.processSupervisor.activePort)")
                statusRow("Database", viewModel.processSupervisor.databaseURL)
                statusRow("uv Executable", viewModel.processSupervisor.uvExecutablePath.isEmpty ? "n/a" : viewModel.processSupervisor.uvExecutablePath)
                statusRow("Current Version", viewModel.updateService.currentVersion())
                if let latest = viewModel.updateService.latestVersion {
                    statusRow(
                        "Latest Release",
                        viewModel.updateService.updateAvailable() ? "\(latest) available" : "\(latest) installed"
                    )
                }
                if let releaseURL = viewModel.updateService.releaseURL {
                    Button("Open Release Page") {
                        viewModel.updateService.openReleasePage()
                    }
                    .help(releaseURL.absoluteString)
                }
                if !viewModel.updateService.errorMessage.isEmpty {
                    Text(viewModel.updateService.errorMessage)
                        .foregroundStyle(.orange)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        } label: {
            Label("Engine Supervisor", systemImage: "terminal")
        }
    }

    private var overviewGrid: some View {
        LazyVGrid(columns: [
            GridItem(.flexible()),
            GridItem(.flexible()),
        ], spacing: 16) {
            GroupBox {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Health")
                        .font(.headline)
                    if let health = viewModel.health {
                        statusRow("Status", health.status)
                        statusRow("Service", health.service)
                        statusRow("Environment", health.environment)
                    } else {
                        Text("Waiting for engine health...")
                            .foregroundStyle(.secondary)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }

            GroupBox {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Operator")
                        .font(.headline)
                    if let operatorStatus = viewModel.operatorStatus {
                        statusRow("Total Runs", "\(operatorStatus.totalRuns)")
                        statusRow("Running", "\(operatorStatus.runningRuns)")
                        statusRow("Healthy", "\(operatorStatus.healthyRunningRuns)")
                        statusRow("Stalled", "\(operatorStatus.stalledRuns)")
                    } else {
                        Text("Waiting for operator status...")
                            .foregroundStyle(.secondary)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }

            GroupBox {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Agent")
                        .font(.headline)
                    if let agent = viewModel.agentStatus {
                        statusRow("Adapter", agent.name)
                        statusRow("Available", agent.available ? "yes" : "no")
                        statusRow("Executable", agent.resolvedExecutable ?? agent.executable)
                    } else {
                        Text("Waiting for agent status...")
                            .foregroundStyle(.secondary)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }

            GroupBox {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Providers")
                        .font(.headline)
                    if viewModel.providers.isEmpty {
                        Text("No providers loaded yet.")
                            .foregroundStyle(.secondary)
                    } else {
                        ForEach(viewModel.providers) { provider in
                            VStack(alignment: .leading, spacing: 2) {
                                Text(provider.name)
                                    .fontWeight(.semibold)
                                Text("\(provider.kind) / \(provider.reachable ? "reachable" : "unreachable")")
                                    .font(.caption)
                                    .foregroundStyle(provider.reachable ? .green : .orange)
                                if let count = provider.modelCount {
                                    Text("models: \(count)")
                                        .font(.caption2)
                                        .foregroundStyle(.secondary)
                                }
                            }
                        }
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
    }

    private var runsSection: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 12) {
                Text("Recent Runs")
                    .font(.headline)
                if viewModel.runs.isEmpty {
                    Text("No runs loaded yet.")
                        .foregroundStyle(.secondary)
                } else {
                    ForEach(viewModel.runs.prefix(12)) { run in
                        VStack(alignment: .leading, spacing: 4) {
                            HStack {
                                Text("#\(run.id) \(run.title)")
                                    .fontWeight(.semibold)
                                Spacer()
                                Text(run.status)
                                    .foregroundStyle(color(for: run.status))
                            }
                            Text("\(run.projectKey) / \(run.metricDirection) / \(run.ratchetDecision)")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                            if let metric = run.metricValue {
                                Text("metric: \(String(format: "%.6f", metric))")
                                    .font(.caption2)
                            }
                            if let summary = run.resultSummary {
                                Text(summary)
                                    .font(.caption2)
                                    .foregroundStyle(.secondary)
                            }
                        }
                        if run.id != viewModel.runs.prefix(12).last?.id {
                            Divider()
                        }
                    }
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        } label: {
            Label("Runs", systemImage: "list.bullet.rectangle")
        }
    }

    private var recoverySection: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 12) {
                Text("Recovery")
                    .font(.headline)
                if let operatorStatus = viewModel.operatorStatus, !operatorStatus.recoverableRuns.isEmpty {
                    ForEach(operatorStatus.recoverableRuns) { run in
                        VStack(alignment: .leading, spacing: 6) {
                            HStack {
                                VStack(alignment: .leading, spacing: 2) {
                                    Text("#\(run.id) \(run.title)")
                                        .fontWeight(.semibold)
                                    Text("\(run.projectKey) / checkpoint \(run.bestRunId.map(String.init) ?? "n/a")")
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                                Spacer()
                                Button("Resume") {
                                    viewModel.resumeRun(run.id)
                                }
                                .disabled(!run.resumable)
                            }
                            Text("status: \(run.status) · stalled: \(run.stalled ? "yes" : "no") · resumes: \(run.resumeCount)")
                                .font(.caption2)
                                .foregroundStyle(.secondary)
                            if let error = run.errorMessage, !error.isEmpty {
                                Text(error)
                                    .font(.caption2)
                                    .foregroundStyle(.orange)
                            }
                        }
                        if run.id != operatorStatus.recoverableRuns.last?.id {
                            Divider()
                        }
                    }
                } else {
                    Text("No recoverable runs currently require action.")
                        .foregroundStyle(.secondary)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        } label: {
            Label("Recovery Actions", systemImage: "arrow.clockwise")
        }
    }

    private var logsSection: some View {
        GroupBox {
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 6) {
                    ForEach(Array(viewModel.processSupervisor.logs.enumerated()), id: \.offset) { _, line in
                        Text(line)
                            .font(.system(.caption, design: .monospaced))
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .textSelection(.enabled)
                    }
                }
            }
            .frame(minHeight: 220, maxHeight: 420)
        } label: {
            Label("Engine Logs", systemImage: "doc.text")
        }
    }

    private func statusRow(_ title: String, _ value: String) -> some View {
        HStack(alignment: .top) {
            Text(title)
                .foregroundStyle(.secondary)
                .frame(width: 120, alignment: .leading)
            Text(value)
                .textSelection(.enabled)
            Spacer()
        }
        .font(.caption)
    }

    private func errorBanner(_ message: String) -> some View {
        HStack {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundStyle(.yellow)
            Text(message)
                .font(.caption)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.yellow.opacity(0.12))
        .clipShape(RoundedRectangle(cornerRadius: 10))
    }

    private func color(for status: String) -> Color {
        switch status.lowercased() {
        case "accepted", "succeeded":
            return .green
        case "rejected":
            return .orange
        case "failed":
            return .red
        default:
            return .secondary
        }
    }
}
