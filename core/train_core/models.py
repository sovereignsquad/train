from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from train_core.db import Base
from train_core.time import utc_now


class MetricDirection(StrEnum):
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class RatchetDecision(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    NOT_APPLICABLE = "not_applicable"


class GitAction(StrEnum):
    NONE = "none"
    COMMITTED = "committed"
    RESTORED = "restored"
    BLOCKED = "blocked"


class RunRecord(Base):
    __tablename__ = "run_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_key: Mapped[str] = mapped_column(String(120), index=True)
    title: Mapped[str] = mapped_column(String(200))
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    metric_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    metric_direction: Mapped[MetricDirection] = mapped_column(
        Enum(MetricDirection),
        default=MetricDirection.MINIMIZE,
    )
    metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    budget_seconds: Mapped[int] = mapped_column(Integer, default=300)
    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus),
        default=RunStatus.PENDING,
        index=True,
    )
    mutable_artifact: Mapped[str | None] = mapped_column(String(260), nullable=True)
    runner_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ratchet_decision: Mapped[RatchetDecision] = mapped_column(
        Enum(RatchetDecision),
        default=RatchetDecision.NOT_APPLICABLE,
    )
    git_action: Mapped[GitAction] = mapped_column(
        Enum(GitAction),
        default=GitAction.NONE,
    )
    best_metric_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    best_metric_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    git_head_before: Mapped[str | None] = mapped_column(String(120), nullable=True)
    git_head_after: Mapped[str | None] = mapped_column(String(120), nullable=True)
    git_worktree_dirty: Mapped[bool | None] = mapped_column(nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resumed_from_run_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resume_count: Mapped[int] = mapped_column(Integer, default=0)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
    )


class ProjectState(Base):
    __tablename__ = "project_states"

    project_key: Mapped[str] = mapped_column(String(120), primary_key=True)
    metric_name: Mapped[str] = mapped_column(String(120))
    metric_direction: Mapped[MetricDirection] = mapped_column(Enum(MetricDirection))
    best_run_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    best_metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_run_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    git_head: Mapped[str | None] = mapped_column(String(120), nullable=True)
    git_worktree_dirty: Mapped[bool | None] = mapped_column(nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
    )


class ManagedProject(Base):
    __tablename__ = "managed_projects"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    mutable_artifact: Mapped[str] = mapped_column(String(260))
    autonomous_mutable_artifacts_json: Mapped[str] = mapped_column(Text)
    setup_artifacts_json: Mapped[str] = mapped_column(Text)
    dependency_artifacts_json: Mapped[str] = mapped_column(Text)
    metric_name: Mapped[str] = mapped_column(String(120))
    metric_direction: Mapped[MetricDirection] = mapped_column(Enum(MetricDirection))
    min_budget_seconds: Mapped[int] = mapped_column(Integer)
    default_budget_seconds: Mapped[int] = mapped_column(Integer)
    max_budget_seconds: Mapped[int] = mapped_column(Integer)
    runner_key: Mapped[str] = mapped_column(String(120))
    execution_entrypoint: Mapped[str] = mapped_column(String(260))
    template_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
    )


class EvalDatasetRecord(Base):
    __tablename__ = "eval_datasets"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    version: Mapped[str] = mapped_column(String(160), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    source_kind: Mapped[str] = mapped_column(String(40))
    scope_kind: Mapped[str] = mapped_column(String(40))
    scope_value: Mapped[str | None] = mapped_column(String(120), nullable=True)
    items_json: Mapped[str] = mapped_column(Text)
    provenance_json: Mapped[str] = mapped_column(Text)
    item_count: Mapped[int] = mapped_column(Integer)
    fingerprint: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
    )


class EvalDatasetSliceRecord(Base):
    __tablename__ = "eval_dataset_slices"

    dataset_key: Mapped[str] = mapped_column(String(120), primary_key=True)
    dataset_version: Mapped[str] = mapped_column(String(160), primary_key=True)
    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    version: Mapped[str] = mapped_column(String(160), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    scope_kind: Mapped[str] = mapped_column(String(40))
    scope_value: Mapped[str | None] = mapped_column(String(120), nullable=True)
    selection_item_keys_json: Mapped[str] = mapped_column(Text)
    provenance_json: Mapped[str] = mapped_column(Text)
    item_count: Mapped[int] = mapped_column(Integer)
    fingerprint: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
    )


class GraderSuiteRecord(Base):
    __tablename__ = "grader_suites"

    dataset_key: Mapped[str] = mapped_column(String(120), primary_key=True)
    dataset_version: Mapped[str] = mapped_column(String(160), primary_key=True)
    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    version: Mapped[str] = mapped_column(String(160), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    proposal_family: Mapped[str] = mapped_column(String(120), index=True)
    graders_json: Mapped[str] = mapped_column(Text)
    provenance_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
    )


class TrainingSpecRecord(Base):
    __tablename__ = "training_specs"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    version: Mapped[str] = mapped_column(String(160), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    dataset_key: Mapped[str] = mapped_column(String(120), index=True)
    dataset_version: Mapped[str] = mapped_column(String(160))
    dataset_slice_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    dataset_slice_version: Mapped[str | None] = mapped_column(String(160), nullable=True)
    grader_suite_key: Mapped[str] = mapped_column(String(120))
    grader_suite_version: Mapped[str] = mapped_column(String(160))
    base_model_ref: Mapped[str] = mapped_column(String(260))
    base_model_source_kind: Mapped[str] = mapped_column(String(40), default="huggingface")
    template_ref: Mapped[str] = mapped_column(String(260))
    tokenizer_ref: Mapped[str | None] = mapped_column(String(260), nullable=True)
    training_backend: Mapped[str] = mapped_column(String(40), index=True)
    training_stage: Mapped[str] = mapped_column(String(40))
    training_method: Mapped[str] = mapped_column(String(40))
    expected_adapter_family: Mapped[str] = mapped_column(String(120), index=True)
    output_dir: Mapped[str] = mapped_column(String(520))
    hyperparameters_json: Mapped[str] = mapped_column(Text)
    provenance_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
    )


class AdapterArtifactRecord(Base):
    __tablename__ = "adapter_artifacts"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    version: Mapped[str] = mapped_column(String(160), primary_key=True)
    training_spec_key: Mapped[str] = mapped_column(String(120), index=True)
    training_spec_version: Mapped[str] = mapped_column(String(160))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    dataset_key: Mapped[str] = mapped_column(String(120), index=True)
    dataset_version: Mapped[str] = mapped_column(String(160))
    dataset_slice_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    dataset_slice_version: Mapped[str | None] = mapped_column(String(160), nullable=True)
    grader_suite_key: Mapped[str] = mapped_column(String(120))
    grader_suite_version: Mapped[str] = mapped_column(String(160))
    base_model_ref: Mapped[str] = mapped_column(String(260))
    base_model_source_kind: Mapped[str] = mapped_column(String(40), default="huggingface")
    template_ref: Mapped[str] = mapped_column(String(260))
    tokenizer_ref: Mapped[str | None] = mapped_column(String(260), nullable=True)
    training_backend: Mapped[str] = mapped_column(String(40), index=True)
    training_stage: Mapped[str] = mapped_column(String(40))
    training_method: Mapped[str] = mapped_column(String(40))
    adapter_family: Mapped[str] = mapped_column(String(120), index=True)
    adapter_format: Mapped[str] = mapped_column(String(40))
    artifact_path: Mapped[str] = mapped_column(String(520))
    checkpoint_path: Mapped[str | None] = mapped_column(String(520), nullable=True)
    training_log_path: Mapped[str | None] = mapped_column(String(520), nullable=True)
    packaging_metadata_path: Mapped[str | None] = mapped_column(String(520), nullable=True)
    provenance_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
    )
