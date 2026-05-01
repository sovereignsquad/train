from __future__ import annotations

from datetime import timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from train_core.db import Base
from train_core.models import MetricDirection, ProjectState, RunRecord, RunStatus
from train_core.operator import build_operator_snapshot, resume_run_record, touch_run_heartbeat
from train_core.time import utc_now


def build_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return session_factory()


def test_operator_snapshot_reports_stalled_and_recoverable_runs() -> None:
    db = build_session()
    try:
        state = ProjectState(
            project_key="mythology",
            metric_name="val_bpb",
            metric_direction=MetricDirection.MINIMIZE,
            best_run_id=1,
            best_metric_value=3.5,
            last_run_id=2,
            git_head="abc123",
            git_worktree_dirty=False,
        )
        stalled_run = RunRecord(
            id=2,
            project_key="mythology",
            title="Stalled run",
            metric_name="val_bpb",
            metric_direction=MetricDirection.MINIMIZE,
            budget_seconds=300,
            status=RunStatus.RUNNING,
            mutable_artifact="projects/mythology/train.py",
            runner_key="python-benchmark",
            started_at=utc_now() - timedelta(minutes=10),
            heartbeat_at=utc_now() - timedelta(minutes=10),
            lease_expires_at=utc_now() - timedelta(minutes=1),
            resume_count=0,
        )
        db.add(state)
        db.add(stalled_run)
        db.commit()

        snapshot = build_operator_snapshot(db)

        assert snapshot.total_runs == 1
        assert snapshot.running_runs == 1
        assert snapshot.healthy_running_runs == 0
        assert snapshot.stalled_runs == 1
        assert len(snapshot.recoverable_runs) == 1
        assert snapshot.recoverable_runs[0].resumable is True
        assert snapshot.recoverable_runs[0].checkpoint_git_head == "abc123"
    finally:
        db.close()


def test_resume_run_creates_new_pending_run_from_known_good_checkpoint() -> None:
    db = build_session()
    try:
        state = ProjectState(
            project_key="mythology",
            metric_name="val_bpb",
            metric_direction=MetricDirection.MINIMIZE,
            best_run_id=1,
            best_metric_value=3.4,
            last_run_id=2,
            git_head="abc123",
            git_worktree_dirty=False,
        )
        failed_run = RunRecord(
            id=2,
            project_key="mythology",
            title="Failed run",
            metric_name="val_bpb",
            metric_direction=MetricDirection.MINIMIZE,
            budget_seconds=300,
            status=RunStatus.FAILED,
            mutable_artifact="projects/mythology/train.py",
            runner_key="python-benchmark",
            error_message="context exhausted",
            resume_count=0,
        )
        db.add(state)
        db.add(failed_run)
        db.commit()

        resumed = resume_run_record(db, failed_run)

        assert resumed.status == RunStatus.PENDING
        assert resumed.resumed_from_run_id == failed_run.id
        assert resumed.resume_count == 1
        assert "known-good checkpoint run 1" in (resumed.result_summary or "")
    finally:
        db.close()


def test_heartbeat_extends_running_run_lease() -> None:
    db = build_session()
    try:
        run = RunRecord(
            id=1,
            project_key="mythology",
            title="Running run",
            metric_name="val_bpb",
            metric_direction=MetricDirection.MINIMIZE,
            budget_seconds=300,
            status=RunStatus.RUNNING,
            mutable_artifact="projects/mythology/train.py",
            runner_key="python-benchmark",
            started_at=utc_now() - timedelta(seconds=30),
            heartbeat_at=utc_now() - timedelta(seconds=30),
            lease_expires_at=utc_now() - timedelta(seconds=1),
            resume_count=0,
        )
        db.add(run)
        db.commit()

        updated = touch_run_heartbeat(db, run, lease_seconds=120)

        assert updated.heartbeat_at is not None
        assert updated.lease_expires_at is not None
        assert updated.lease_expires_at > updated.heartbeat_at
        assert (updated.lease_expires_at - updated.heartbeat_at).total_seconds() == 120
    finally:
        db.close()
