import subprocess

from sqlalchemy.orm import Session

from autotrain_core.config import ROOT_DIR
from autotrain_core.models import MetricDirection, ProjectState, RatchetDecision, RunRecord, RunStatus


class RatchetError(ValueError):
    """Raised when a ratchet decision cannot be applied."""


def apply_ratchet_decision(db: Session, run: RunRecord) -> RunRecord:
    if run.status not in {RunStatus.SUCCEEDED, RunStatus.ACCEPTED, RunStatus.REJECTED}:
        raise RatchetError("Only successful terminal runs can be evaluated by the ratchet")
    if run.metric_value is None:
        raise RatchetError("A metric value is required for ratchet evaluation")

    git_head, git_dirty = get_git_state()
    project_state = db.get(ProjectState, run.project_key)

    if project_state is None:
        project_state = ProjectState(
            project_key=run.project_key,
            metric_name=run.metric_name or "metric",
            metric_direction=run.metric_direction,
            best_run_id=run.id,
            best_metric_value=run.metric_value,
            last_run_id=run.id,
            git_head=git_head,
            git_worktree_dirty=git_dirty,
        )
        run.best_metric_before = None
        run.best_metric_after = run.metric_value
        run.ratchet_decision = RatchetDecision.ACCEPTED
        run.status = RunStatus.ACCEPTED
    else:
        run.best_metric_before = project_state.best_metric_value
        run.ratchet_decision = (
            RatchetDecision.ACCEPTED
            if is_better_metric(
                candidate=run.metric_value,
                incumbent=project_state.best_metric_value,
                direction=project_state.metric_direction,
            )
            else RatchetDecision.REJECTED
        )

        project_state.last_run_id = run.id
        project_state.git_head = git_head
        project_state.git_worktree_dirty = git_dirty

        if run.ratchet_decision == RatchetDecision.ACCEPTED:
            project_state.best_run_id = run.id
            project_state.best_metric_value = run.metric_value
            run.status = RunStatus.ACCEPTED
        else:
            run.status = RunStatus.REJECTED

        run.best_metric_after = project_state.best_metric_value

    run.git_head_before = git_head
    run.git_head_after = git_head
    run.git_worktree_dirty = git_dirty

    db.add(project_state)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def is_better_metric(candidate: float, incumbent: float | None, direction: MetricDirection) -> bool:
    if incumbent is None:
        return True
    if direction == MetricDirection.MINIMIZE:
        return candidate < incumbent
    return candidate > incumbent


def get_git_state() -> tuple[str | None, bool | None]:
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:
        head = None

    try:
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return head, bool(dirty)
    except Exception:
        return head, None
