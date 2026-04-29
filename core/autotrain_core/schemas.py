from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from autotrain_core.models import GitAction, MetricDirection, RatchetDecision, RunStatus


class RunCreate(BaseModel):
    project_key: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=200)
    objective: str | None = None
    metric_name: str | None = Field(default=None, max_length=120)
    metric_direction: MetricDirection | None = None
    budget_seconds: int | None = Field(default=None, ge=1, le=86_400)


class RunStart(BaseModel):
    pass


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
    metric_name: str
    metric_direction: MetricDirection
    default_budget_seconds: int
    runner_key: str
    execution_entrypoint: str


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
    finished_at: datetime | None
    result_summary: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

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
