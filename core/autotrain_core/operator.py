from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from autotrain_core.config import settings
from autotrain_core.models import ProjectState, RunRecord, RunStatus
from autotrain_core.time import utc_now


class OperatorError(ValueError):
    """Raised when an operator control action is invalid."""


@dataclass(frozen=True)
class RecoverableRun:
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


@dataclass(frozen=True)
class OperatorSnapshot:
    generated_at: datetime
    total_runs: int
    running_runs: int
    healthy_running_runs: int
    stalled_runs: int
    recoverable_runs: tuple[RecoverableRun, ...]


def _resolve_lease_seconds(run: RunRecord, lease_seconds: int | None = None) -> int:
    if lease_seconds is not None:
        return lease_seconds
    return run.budget_seconds + settings.operator_lease_grace_seconds


def is_run_stalled(run: RunRecord, now: datetime | None = None) -> bool:
    if run.status != RunStatus.RUNNING:
        return False
    if run.lease_expires_at is None:
        return False
    return run.lease_expires_at < (now or utc_now())


def touch_run_heartbeat(db: Session, run: RunRecord, lease_seconds: int | None = None) -> RunRecord:
    if run.status != RunStatus.RUNNING:
        raise OperatorError("Only running runs can receive a heartbeat")

    heartbeat_at = utc_now()
    run.heartbeat_at = heartbeat_at
    run.lease_expires_at = heartbeat_at + timedelta(seconds=_resolve_lease_seconds(run, lease_seconds))
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def build_operator_snapshot(db: Session) -> OperatorSnapshot:
    now = utc_now()
    runs = list(db.scalars(select(RunRecord).order_by(RunRecord.created_at.desc())))
    project_states = {
        state.project_key: state
        for state in db.scalars(select(ProjectState).order_by(ProjectState.project_key.asc()))
    }

    running_runs = [run for run in runs if run.status == RunStatus.RUNNING]
    stalled_runs = [run for run in running_runs if is_run_stalled(run, now)]
    healthy_running_runs = [run for run in running_runs if not is_run_stalled(run, now)]

    recoverable: list[RecoverableRun] = []
    for run in runs:
        state = project_states.get(run.project_key)
        stalled = is_run_stalled(run, now)
        resumable = state is not None and state.best_run_id is not None and (
            stalled or run.status == RunStatus.FAILED
        )
        if not resumable:
            continue
        recoverable.append(
            RecoverableRun(
                id=run.id,
                project_key=run.project_key,
                title=run.title,
                status=run.status,
                stalled=stalled,
                resumable=resumable,
                resume_count=run.resume_count,
                resumed_from_run_id=run.resumed_from_run_id,
                heartbeat_at=run.heartbeat_at,
                lease_expires_at=run.lease_expires_at,
                best_run_id=state.best_run_id,
                checkpoint_git_head=state.git_head,
                error_message=run.error_message,
                updated_at=run.updated_at,
            )
        )

    return OperatorSnapshot(
        generated_at=now,
        total_runs=len(runs),
        running_runs=len(running_runs),
        healthy_running_runs=len(healthy_running_runs),
        stalled_runs=len(stalled_runs),
        recoverable_runs=tuple(recoverable),
    )


def resume_run_record(db: Session, run: RunRecord) -> RunRecord:
    state = db.get(ProjectState, run.project_key)
    if state is None or state.best_run_id is None:
        raise OperatorError("No known-good checkpoint exists for this project")

    stalled = is_run_stalled(run)
    if run.status == RunStatus.RUNNING and not stalled:
        raise OperatorError("Only stalled or failed runs can be resumed")
    if run.status not in {RunStatus.RUNNING, RunStatus.FAILED}:
        raise OperatorError("Only stalled or failed runs can be resumed")

    concurrent = list(
        db.scalars(
            select(RunRecord).where(
                RunRecord.project_key == run.project_key,
                RunRecord.status == RunStatus.RUNNING,
                RunRecord.id != run.id,
            )
        )
    )
    if concurrent:
        raise OperatorError("Another run for this project is already active")

    if run.status == RunStatus.RUNNING:
        run.status = RunStatus.FAILED
        run.finished_at = utc_now()
        run.error_message = run.error_message or "Run marked failed by operator resume after lease expiry"
        run.result_summary = (
            run.result_summary or "Operator resume marked the stalled run failed before spawning a replacement"
        )
        db.add(run)

    resumed = RunRecord(
        project_key=run.project_key,
        title=f"{run.title} (resume {run.resume_count + 1})",
        objective=run.objective,
        metric_name=run.metric_name,
        metric_direction=run.metric_direction,
        budget_seconds=run.budget_seconds,
        status=RunStatus.PENDING,
        mutable_artifact=run.mutable_artifact,
        runner_key=run.runner_key,
        resumed_from_run_id=run.id,
        resume_count=run.resume_count + 1,
        result_summary=(
            f"Resumed from run {run.id} using known-good checkpoint run {state.best_run_id}"
        ),
    )
    db.add(resumed)
    db.commit()
    db.refresh(resumed)
    return resumed
