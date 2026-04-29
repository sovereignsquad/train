from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from autotrain_core.db import Base


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
    best_metric_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    best_metric_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    git_head_before: Mapped[str | None] = mapped_column(String(120), nullable=True)
    git_head_after: Mapped[str | None] = mapped_column(String(120), nullable=True)
    git_worktree_dirty: Mapped[bool | None] = mapped_column(nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
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
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
