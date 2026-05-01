import subprocess

from sqlalchemy.orm import Session

from train_core.config import ROOT_DIR
from train_core.guardrails import GuardrailError, validate_autonomous_workspace
from train_core.models import (
    GitAction,
    MetricDirection,
    ProjectState,
    RatchetDecision,
    RunRecord,
    RunStatus,
)
from train_core.projects import get_project

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
    run.git_worktree_dirty = git_dirty

    try:
        _apply_git_mutation(run)
    except RatchetError as exc:
        _persist_blocked_ratchet_state(db, run, project_state, str(exc), git_head)
        raise

    git_head_after, git_dirty_after = get_git_state()
    run.git_head_after = git_head_after
    run.git_worktree_dirty = git_dirty_after
    project_state.git_head = git_head_after
    project_state.git_worktree_dirty = git_dirty_after

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


def _apply_git_mutation(run: RunRecord) -> None:
    if not run.mutable_artifact:
        run.git_action = GitAction.NONE
        return

    changed_paths = get_changed_paths()
    project = get_project(run.project_key)
    if project is None:
        raise RatchetError(f"Unknown project '{run.project_key}'")

    try:
        validate_autonomous_workspace(project, changed_paths)
    except GuardrailError as exc:
        run.git_action = GitAction.BLOCKED
        raise RatchetError(str(exc)) from exc

    if not changed_paths:
        run.git_action = GitAction.NONE
        return

    allowed_path = run.mutable_artifact

    if run.ratchet_decision == RatchetDecision.ACCEPTED:
        commit_mutable_artifact(allowed_path, run)
        run.git_action = GitAction.COMMITTED
        return

    if run.ratchet_decision == RatchetDecision.REJECTED:
        restore_mutable_artifact(allowed_path)
        run.git_action = GitAction.RESTORED
        return

    run.git_action = GitAction.NONE


def get_changed_paths() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=True,
    )
    paths: list[str] = []
    for raw_line in result.stdout.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path)
    return paths


def commit_mutable_artifact(path: str, run: RunRecord) -> None:
    subprocess.run(["git", "add", path], cwd=ROOT_DIR, check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            f"ratchet: accept run {run.id} for {run.project_key}",
        ],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=True,
    )


def restore_mutable_artifact(path: str) -> None:
    subprocess.run(["git", "restore", "--", path], cwd=ROOT_DIR, check=True)


def _persist_blocked_ratchet_state(
    db: Session,
    run: RunRecord,
    project_state: ProjectState | None,
    message: str,
    git_head_before: str | None,
) -> None:
    git_head_after, git_dirty_after = get_git_state()
    run.git_action = GitAction.BLOCKED
    run.error_message = message
    run.git_head_before = git_head_before
    run.git_head_after = git_head_after
    run.git_worktree_dirty = git_dirty_after

    if project_state is not None:
        project_state.git_head = git_head_after
        project_state.git_worktree_dirty = git_dirty_after
        db.add(project_state)

    db.add(run)
    db.commit()
