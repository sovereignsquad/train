from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from train_core.agents import AgentMode
from train_core.models import GitAction, MetricDirection, RatchetDecision, RunStatus
from train_core.providers import ProviderKind


class RunCreate(BaseModel):
    project_key: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=200)
    objective: str | None = None
    metric_name: str | None = Field(default=None, max_length=120)
    metric_direction: MetricDirection | None = None
    budget_seconds: int | None = Field(default=None, ge=1, le=86_400)


class RunStart(BaseModel):
    pass


class RunHeartbeat(BaseModel):
    lease_seconds: int | None = Field(default=None, ge=5, le=86_400)


class RunComplete(BaseModel):
    status: RunStatus
    metric_value: float | None = None
    result_summary: str | None = None
    error_message: str | None = None

    @model_validator(mode="after")
    def validate_terminal_payload(self) -> "RunComplete":
        if self.status not in {RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.ACCEPTED, RunStatus.REJECTED}:
            raise ValueError("Completion status must be a terminal run status")
        if self.status in {RunStatus.SUCCEEDED, RunStatus.ACCEPTED, RunStatus.REJECTED} and self.metric_value is None:
            raise ValueError("A metric value is required for successful terminal statuses")
        if self.status == RunStatus.FAILED and not self.error_message:
            raise ValueError("An error message is required when marking a run as failed")
        return self


class ProjectRead(BaseModel):
    key: str
    name: str
    description: str
    mutable_artifact: str
    autonomous_mutable_artifacts: tuple[str, ...]
    setup_artifacts: tuple[str, ...]
    dependency_artifacts: tuple[str, ...]
    metric_name: str
    metric_direction: MetricDirection
    min_budget_seconds: int
    default_budget_seconds: int
    max_budget_seconds: int
    runner_key: str
    execution_entrypoint: str
    source_kind: str
    editable: bool
    deletable: bool
    template_key: str | None


class ProjectWrite(BaseModel):
    key: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    mutable_artifact: str = Field(min_length=1, max_length=260)
    autonomous_mutable_artifacts: tuple[str, ...] = Field(min_length=1)
    setup_artifacts: tuple[str, ...] = Field(min_length=1)
    dependency_artifacts: tuple[str, ...] = Field(min_length=1)
    metric_name: str = Field(min_length=1, max_length=120)
    metric_direction: MetricDirection
    min_budget_seconds: int = Field(ge=1, le=86_400)
    default_budget_seconds: int = Field(ge=1, le=86_400)
    max_budget_seconds: int = Field(ge=1, le=86_400)
    runner_key: str = Field(min_length=1, max_length=120)
    execution_entrypoint: str = Field(min_length=1, max_length=260)
    template_key: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def validate_project_budgets(self) -> "ProjectWrite":
        if self.min_budget_seconds > self.default_budget_seconds:
            raise ValueError("Default budget must be greater than or equal to min budget")
        if self.default_budget_seconds > self.max_budget_seconds:
            raise ValueError("Default budget must be less than or equal to max budget")
        return self


class ProjectBootstrapRequest(BaseModel):
    overwrite: bool = False


class ProjectBootstrapRead(BaseModel):
    project_key: str
    project_root: str
    created_files: tuple[str, ...]
    overwritten_files: tuple[str, ...]
    skipped_files: tuple[str, ...]


class ExecutionResult(BaseModel):
    status: RunStatus
    metric_value: float | None = None
    result_summary: str | None = None
    error_message: str | None = None


class RunRead(BaseModel):
    id: int
    project_key: str
    title: str
    objective: str | None
    metric_name: str | None
    metric_direction: MetricDirection
    metric_value: float | None
    budget_seconds: int
    status: RunStatus
    mutable_artifact: str | None
    runner_key: str | None
    ratchet_decision: RatchetDecision
    git_action: GitAction
    best_metric_before: float | None
    best_metric_after: float | None
    git_head_before: str | None
    git_head_after: str | None
    git_worktree_dirty: bool | None
    started_at: datetime | None
    heartbeat_at: datetime | None
    lease_expires_at: datetime | None
    finished_at: datetime | None
    resumed_from_run_id: int | None
    resume_count: int
    result_summary: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecoverableRunRead(BaseModel):
    id: int
    project_key: str
    title: str
    status: RunStatus
    stalled: bool
    resumable: bool
    resume_count: int
    resumed_from_run_id: int | None
    heartbeat_at: datetime | None
    lease_expires_at: datetime | None
    best_run_id: int | None
    checkpoint_git_head: str | None
    error_message: str | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class OperatorStatusRead(BaseModel):
    generated_at: datetime
    total_runs: int
    running_runs: int
    healthy_running_runs: int
    stalled_runs: int
    recoverable_runs: list[RecoverableRunRead]

    model_config = {"from_attributes": True}


class ProjectStateRead(BaseModel):
    project_key: str
    metric_name: str
    metric_direction: MetricDirection
    best_run_id: int | None
    best_metric_value: float | None
    last_run_id: int | None
    git_head: str | None
    git_worktree_dirty: bool | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentAdapterRead(BaseModel):
    key: str
    name: str
    description: str
    executable: str
    first_class: bool


class AgentStatusRead(BaseModel):
    key: str
    name: str
    available: bool
    executable: str
    resolved_executable: str | None
    version: str | None
    mistral_api_key_configured: bool
    contract_home: str
    runtime_home: str
    config_path: str
    agent_config_path: str
    prompt_path: str
    issues: list[str]


class AgentLaunchPlanRead(BaseModel):
    adapter_key: str
    project_key: str
    mode: AgentMode
    command: list[str]
    prompt: str
    workdir: str
    environment: dict[str, str]
    summary: str


class ProviderAdapterRead(BaseModel):
    key: str
    name: str
    kind: ProviderKind
    description: str
    base_url: str
    requires_api_key: bool


class ProviderStatusRead(BaseModel):
    key: str
    name: str
    kind: ProviderKind
    base_url: str
    configured: bool
    reachable: bool
    model_count: int | None
    models: tuple[str, ...]
    issues: list[str]
