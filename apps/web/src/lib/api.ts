const DEFAULT_API_URL = "http://127.0.0.1:8000";

export type HealthPayload = {
  status: string;
  service: string;
  environment: string;
};

export type ProjectPayload = {
  key: string;
  name: string;
  description: string;
  mutable_artifact: string;
  metric_name: string;
  metric_direction: string;
  default_budget_seconds: number;
  runner_key: string;
  execution_entrypoint: string;
};

export type RunPayload = {
  id: number;
  project_key: string;
  title: string;
  metric_name: string | null;
  metric_direction: string;
  metric_value: number | null;
  budget_seconds: number;
  status: string;
  mutable_artifact: string | null;
  runner_key: string | null;
  ratchet_decision: string;
  git_action: string;
  result_summary: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
};

export type ProjectStatePayload = {
  project_key: string;
  metric_name: string;
  metric_direction: string;
  best_run_id: number | null;
  best_metric_value: number | null;
  last_run_id: number | null;
  git_head: string | null;
  git_worktree_dirty: boolean | null;
  updated_at: string;
};

export type AgentStatusPayload = {
  key: string;
  name: string;
  available: boolean;
  executable: string;
  resolved_executable: string | null;
  version: string | null;
  mistral_api_key_configured: boolean;
  contract_home: string;
  runtime_home: string;
  config_path: string;
  agent_config_path: string;
  prompt_path: string;
  issues: string[];
};

export type ProviderPayload = {
  key: string;
  name: string;
  kind: string;
  base_url: string;
  configured: boolean;
  reachable: boolean;
  model_count: number | null;
  models: string[];
  issues: string[];
};

export type RecoverableRunPayload = {
  id: number;
  project_key: string;
  title: string;
  status: string;
  stalled: boolean;
  resumable: boolean;
  resume_count: number;
  resumed_from_run_id: number | null;
  heartbeat_at: string | null;
  lease_expires_at: string | null;
  best_run_id: number | null;
  checkpoint_git_head: string | null;
  error_message: string | null;
  updated_at: string;
};

export type OperatorStatusPayload = {
  generated_at: string;
  total_runs: number;
  running_runs: number;
  healthy_running_runs: number;
  stalled_runs: number;
  recoverable_runs: RecoverableRunPayload[];
};

export type ApiResult<T> = {
  ok: boolean;
  data: T | null;
  error: string | null;
};

export function getApiBaseUrl(): string {
  return process.env.TRAIN_API_URL || DEFAULT_API_URL;
}

async function fetchJson<T>(path: string): Promise<ApiResult<T>> {
  try {
    const response = await fetch(`${getApiBaseUrl()}${path}`, {
      cache: "no-store",
    });
    if (!response.ok) {
      return {
        ok: false,
        data: null,
        error: `${response.status} ${response.statusText}`,
      };
    }

    return {
      ok: true,
      data: (await response.json()) as T,
      error: null,
    };
  } catch (error) {
    return {
      ok: false,
      data: null,
      error: error instanceof Error ? error.message : "Unknown fetch error",
    };
  }
}

export async function getDashboardData() {
  const [health, projects, runs, projectStates, agentStatus, mistralProvider, ollamaProvider, operatorStatus] =
    await Promise.all([
      fetchJson<HealthPayload>("/health"),
      fetchJson<ProjectPayload[]>("/v1/projects"),
      fetchJson<RunPayload[]>("/v1/runs"),
      fetchJson<ProjectStatePayload[]>("/v1/project-states"),
      fetchJson<AgentStatusPayload>("/v1/agents/mistral-vibe"),
      fetchJson<ProviderPayload>("/v1/providers/mistral-api"),
      fetchJson<ProviderPayload>("/v1/providers/ollama"),
      fetchJson<OperatorStatusPayload>("/v1/operator/status"),
    ]);

  return {
    apiBaseUrl: getApiBaseUrl(),
    health,
    projects,
    runs,
    projectStates,
    agentStatus,
    operatorStatus,
    providers: {
      mistral: mistralProvider,
      ollama: ollamaProvider,
    },
  };
}
