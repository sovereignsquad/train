import json
import subprocess
from datetime import timedelta

from sqlalchemy.orm import Session

from train_core.config import ROOT_DIR, settings
from train_core.guardrails import GuardrailError, validate_autonomous_workspace, validate_run_budget
from train_core.models import RunRecord, RunStatus
from train_core.projects import ProjectDefinition, build_run_command, get_project
from train_core.schemas import ExecutionResult, RunComplete, RunCreate
from train_core.time import utc_now


class RunnerError(ValueError):
    """Raised when a run lifecycle transition is invalid."""


def create_run_record(db: Session, payload: RunCreate) -> RunRecord:
    project = get_project(payload.project_key)
    if project is None:
        raise RunnerError(f"Unknown project '{payload.project_key}'")

    budget_seconds = payload.budget_seconds or project.default_budget_seconds
    try:
        validate_run_budget(project, budget_seconds)
    except GuardrailError as exc:
        raise RunnerError(str(exc)) from exc

    run = RunRecord(
        project_key=project.key,
        title=payload.title,
        objective=payload.objective,
        metric_name=payload.metric_name or project.metric_name,
        metric_direction=payload.metric_direction or project.metric_direction,
        budget_seconds=budget_seconds,
        status=RunStatus.PENDING,
        mutable_artifact=project.mutable_artifact,
        runner_key=project.runner_key,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def start_run_record(db: Session, run: RunRecord) -> RunRecord:
    if run.status != RunStatus.PENDING:
        raise RunnerError("Only pending runs can be started")

    started_at = utc_now()
    run.status = RunStatus.RUNNING
    run.started_at = started_at
    run.heartbeat_at = started_at
    run.lease_expires_at = started_at + timedelta(
        seconds=run.budget_seconds + settings.operator_lease_grace_seconds
    )
    run.error_message = None
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def complete_run_record(db: Session, run: RunRecord, payload: RunComplete) -> RunRecord:
    if run.status != RunStatus.RUNNING:
        raise RunnerError("Only running runs can be completed")

    run.metric_value = payload.metric_value
    run.result_summary = payload.result_summary
    run.error_message = payload.error_message
    run.finished_at = utc_now()
    run.heartbeat_at = run.finished_at
    run.lease_expires_at = run.finished_at
    run.status = payload.status
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_project_definition(project_key: str) -> ProjectDefinition:
    project = get_project(project_key)
    if project is None:
        raise RunnerError(f"Unknown project '{project_key}'")
    return project


def execute_run_record(db: Session, run: RunRecord) -> RunRecord:
    project = get_project_definition(run.project_key)
    start_run_record(db, run)
    try:
        validate_autonomous_workspace(project, _get_changed_paths())
    except GuardrailError as exc:
        return complete_run_record(
            db,
            run,
            RunComplete(
                status=RunStatus.FAILED,
                error_message=str(exc),
                result_summary="Autonomous workspace guardrail violation before execution",
            ),
        )

    command = build_run_command(project, budget_seconds=run.budget_seconds, run_id=run.id)

    try:
        completed = subprocess.run(
            command,
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=run.budget_seconds + 5,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return complete_run_record(
            db,
            run,
            RunComplete(
                status=RunStatus.FAILED,
                error_message=f"Run timed out after {run.budget_seconds} seconds",
                result_summary="Timed out during benchmark execution",
            ),
        )

    if completed.returncode != 0:
        error_text = completed.stderr.strip() or completed.stdout.strip() or "Runner process failed"
        return complete_run_record(
            db,
            run,
            RunComplete(
                status=RunStatus.FAILED,
                error_message=error_text,
                result_summary="Benchmark process exited with a non-zero status",
            ),
        )

    result = _parse_execution_result(completed.stdout)
    return complete_run_record(
        db,
        run,
        RunComplete(
            status=result.status,
            metric_value=result.metric_value,
            result_summary=result.result_summary,
            error_message=result.error_message,
        ),
    )


def _parse_execution_result(stdout: str) -> ExecutionResult:
    payload_text = stdout.strip()
    if not payload_text:
        raise RunnerError("Runner process returned no stdout payload")

    last_line = payload_text.splitlines()[-1]
    try:
        payload = json.loads(last_line)
    except json.JSONDecodeError as exc:
        raise RunnerError("Runner process stdout did not end with valid JSON") from exc

    try:
        return ExecutionResult.model_validate(payload)
    except Exception as exc:
        raise RunnerError("Runner process returned an invalid execution payload") from exc


def _get_changed_paths() -> list[str]:
    completed = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=True,
    )
    paths: list[str] = []
    for raw_line in completed.stdout.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path)
    return paths
