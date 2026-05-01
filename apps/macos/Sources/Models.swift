import Foundation

struct HealthPayload: Codable {
    let status: String
    let service: String
    let environment: String
}

struct ProjectPayload: Codable, Identifiable {
    let key: String
    let name: String
    let description: String
    let mutableArtifact: String
    let autonomousMutableArtifacts: [String]
    let setupArtifacts: [String]
    let dependencyArtifacts: [String]
    let metricName: String
    let metricDirection: String
    let minBudgetSeconds: Int
    let defaultBudgetSeconds: Int
    let maxBudgetSeconds: Int
    let runnerKey: String
    let executionEntrypoint: String
    let sourceKind: String
    let editable: Bool
    let deletable: Bool
    let templateKey: String?

    var id: String { key }

    private enum CodingKeys: String, CodingKey {
        case key
        case name
        case description
        case mutableArtifact = "mutable_artifact"
        case autonomousMutableArtifacts = "autonomous_mutable_artifacts"
        case setupArtifacts = "setup_artifacts"
        case dependencyArtifacts = "dependency_artifacts"
        case metricName = "metric_name"
        case metricDirection = "metric_direction"
        case minBudgetSeconds = "min_budget_seconds"
        case defaultBudgetSeconds = "default_budget_seconds"
        case maxBudgetSeconds = "max_budget_seconds"
        case runnerKey = "runner_key"
        case executionEntrypoint = "execution_entrypoint"
        case sourceKind = "source_kind"
        case editable
        case deletable
        case templateKey = "template_key"
    }
}

struct ProjectWritePayload: Codable {
    let key: String
    let name: String
    let description: String
    let mutableArtifact: String
    let autonomousMutableArtifacts: [String]
    let setupArtifacts: [String]
    let dependencyArtifacts: [String]
    let metricName: String
    let metricDirection: String
    let minBudgetSeconds: Int
    let defaultBudgetSeconds: Int
    let maxBudgetSeconds: Int
    let runnerKey: String
    let executionEntrypoint: String
    let templateKey: String?

    private enum CodingKeys: String, CodingKey {
        case key
        case name
        case description
        case mutableArtifact = "mutable_artifact"
        case autonomousMutableArtifacts = "autonomous_mutable_artifacts"
        case setupArtifacts = "setup_artifacts"
        case dependencyArtifacts = "dependency_artifacts"
        case metricName = "metric_name"
        case metricDirection = "metric_direction"
        case minBudgetSeconds = "min_budget_seconds"
        case defaultBudgetSeconds = "default_budget_seconds"
        case maxBudgetSeconds = "max_budget_seconds"
        case runnerKey = "runner_key"
        case executionEntrypoint = "execution_entrypoint"
        case templateKey = "template_key"
    }
}

struct ProjectBootstrapRequestPayload: Codable {
    let overwrite: Bool
}

struct ProjectBootstrapPayload: Codable {
    let projectKey: String
    let projectRoot: String
    let createdFiles: [String]
    let overwrittenFiles: [String]
    let skippedFiles: [String]

    private enum CodingKeys: String, CodingKey {
        case projectKey = "project_key"
        case projectRoot = "project_root"
        case createdFiles = "created_files"
        case overwrittenFiles = "overwritten_files"
        case skippedFiles = "skipped_files"
    }
}

struct RunPayload: Codable, Identifiable {
    let id: Int
    let projectKey: String
    let title: String
    let metricName: String?
    let metricDirection: String
    let metricValue: Double?
    let budgetSeconds: Int
    let status: String
    let mutableArtifact: String?
    let runnerKey: String?
    let ratchetDecision: String
    let gitAction: String
    let resultSummary: String?
    let errorMessage: String?
    let leaseExpiresAt: String?
    let resumedFromRunId: Int?
    let resumeCount: Int
    let updatedAt: String

    private enum CodingKeys: String, CodingKey {
        case id
        case projectKey = "project_key"
        case title
        case metricName = "metric_name"
        case metricDirection = "metric_direction"
        case metricValue = "metric_value"
        case budgetSeconds = "budget_seconds"
        case status
        case mutableArtifact = "mutable_artifact"
        case runnerKey = "runner_key"
        case ratchetDecision = "ratchet_decision"
        case gitAction = "git_action"
        case resultSummary = "result_summary"
        case errorMessage = "error_message"
        case leaseExpiresAt = "lease_expires_at"
        case resumedFromRunId = "resumed_from_run_id"
        case resumeCount = "resume_count"
        case updatedAt = "updated_at"
    }
}

struct ProjectStatePayload: Codable, Identifiable {
    let projectKey: String
    let metricName: String
    let metricDirection: String
    let bestRunId: Int?
    let bestMetricValue: Double?
    let lastRunId: Int?
    let gitHead: String?
    let gitWorktreeDirty: Bool?
    let updatedAt: String

    var id: String { projectKey }

    private enum CodingKeys: String, CodingKey {
        case projectKey = "project_key"
        case metricName = "metric_name"
        case metricDirection = "metric_direction"
        case bestRunId = "best_run_id"
        case bestMetricValue = "best_metric_value"
        case lastRunId = "last_run_id"
        case gitHead = "git_head"
        case gitWorktreeDirty = "git_worktree_dirty"
        case updatedAt = "updated_at"
    }
}

struct ProviderPayload: Codable, Identifiable {
    let key: String
    let name: String
    let kind: String
    let baseURL: String
    let configured: Bool
    let reachable: Bool
    let modelCount: Int?
    let models: [String]
    let issues: [String]

    var id: String { key }

    private enum CodingKeys: String, CodingKey {
        case key
        case name
        case kind
        case baseURL = "base_url"
        case configured
        case reachable
        case modelCount = "model_count"
        case models
        case issues
    }
}

struct AgentStatusPayload: Codable {
    let key: String
    let name: String
    let available: Bool
    let executable: String
    let resolvedExecutable: String?
    let version: String?
    let mistralAPIKeyConfigured: Bool
    let issues: [String]

    private enum CodingKeys: String, CodingKey {
        case key
        case name
        case available
        case executable
        case resolvedExecutable = "resolved_executable"
        case version
        case mistralAPIKeyConfigured = "mistral_api_key_configured"
        case issues
    }
}

struct RecoverableRunPayload: Codable, Identifiable {
    let id: Int
    let projectKey: String
    let title: String
    let status: String
    let stalled: Bool
    let resumable: Bool
    let resumeCount: Int
    let resumedFromRunId: Int?
    let leaseExpiresAt: String?
    let bestRunId: Int?
    let errorMessage: String?

    private enum CodingKeys: String, CodingKey {
        case id
        case projectKey = "project_key"
        case title
        case status
        case stalled
        case resumable
        case resumeCount = "resume_count"
        case resumedFromRunId = "resumed_from_run_id"
        case leaseExpiresAt = "lease_expires_at"
        case bestRunId = "best_run_id"
        case errorMessage = "error_message"
    }
}

struct OperatorStatusPayload: Codable {
    let generatedAt: String
    let totalRuns: Int
    let runningRuns: Int
    let healthyRunningRuns: Int
    let stalledRuns: Int
    let recoverableRuns: [RecoverableRunPayload]

    private enum CodingKeys: String, CodingKey {
        case generatedAt = "generated_at"
        case totalRuns = "total_runs"
        case runningRuns = "running_runs"
        case healthyRunningRuns = "healthy_running_runs"
        case stalledRuns = "stalled_runs"
        case recoverableRuns = "recoverable_runs"
    }
}

struct GitHubRelease: Codable {
    let tagName: String
    let htmlURL: String

    private enum CodingKeys: String, CodingKey {
        case tagName = "tag_name"
        case htmlURL = "html_url"
    }
}
