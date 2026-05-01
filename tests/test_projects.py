import json
import shutil
import subprocess

from train_core.config import ROOT_DIR
from train_core.db import SessionLocal, init_db
from train_core.models import MetricDirection
from train_core.projects import (
    ProjectMutation,
    bootstrap_project_workspace,
    create_managed_project,
    delete_managed_project,
    get_project,
    list_projects,
    update_managed_project,
)
from train_core.ratchet import is_better_metric


def test_project_registry_contains_second_project() -> None:
    keys = {project.key for project in list_projects()}
    assert "mythology" in keys
    assert "helpdesk" in keys
    assert "reply" in keys
    assert "trinity_frontier" in keys

    helpdesk = get_project("helpdesk")
    assert helpdesk is not None
    assert helpdesk.metric_name == "macro_f1"
    assert helpdesk.metric_direction.value == "maximize"
    assert helpdesk.mutable_artifact == "projects/helpdesk/train.py"

    reply = get_project("reply")
    assert reply is not None
    assert reply.metric_name == "draft_score"
    assert reply.metric_direction.value == "maximize"
    assert reply.mutable_artifact == "projects/reply/train.py"

    trinity_frontier = get_project("trinity_frontier")
    assert trinity_frontier is not None
    assert trinity_frontier.metric_name == "ranking_score"
    assert trinity_frontier.metric_direction.value == "maximize"
    assert trinity_frontier.mutable_artifact == "projects/trinity_frontier/train.py"


def test_maximize_metric_direction_accepts_higher_scores() -> None:
    helpdesk = get_project("helpdesk")
    assert helpdesk is not None
    assert is_better_metric(0.82, 0.76, helpdesk.metric_direction) is True
    assert is_better_metric(0.74, 0.76, helpdesk.metric_direction) is False


def test_helpdesk_benchmark_runs_successfully() -> None:
    completed = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "projects/helpdesk/run_benchmark.py",
            "--budget-seconds",
            "60",
            "--run-id",
            "1",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout.strip().splitlines()[-1])
    assert payload["status"] == "succeeded"
    assert payload["metric_value"] >= 0.0


def test_reply_benchmark_runs_successfully() -> None:
    completed = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "projects/reply/run_benchmark.py",
            "--budget-seconds",
            "60",
            "--run-id",
            "1",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout.strip().splitlines()[-1])
    assert payload["status"] == "succeeded"
    assert payload["metric_value"] > 0.0


def test_trinity_frontier_benchmark_runs_successfully() -> None:
    completed = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "projects/trinity_frontier/run_benchmark.py",
            "--budget-seconds",
            "60",
            "--run-id",
            "1",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout.strip().splitlines()[-1])
    assert payload["status"] == "succeeded"
    assert payload["metric_value"] > 0.0


def test_managed_project_crud_overlay() -> None:
    init_db()
    project_key = "test-managed-project"
    mutation = ProjectMutation(
        key=project_key,
        name="Test Managed Project",
        description="Managed project used to verify CRUD behavior.",
        mutable_artifact="projects/custom/train.py",
        autonomous_mutable_artifacts=("projects/custom/train.py",),
        setup_artifacts=("projects/custom/prepare.py", "projects/custom/program.md"),
        dependency_artifacts=("pyproject.toml", "uv.lock"),
        metric_name="score",
        metric_direction=MetricDirection.MAXIMIZE,
        min_budget_seconds=30,
        default_budget_seconds=60,
        max_budget_seconds=120,
        runner_key="python-benchmark",
        execution_entrypoint="projects/custom/run_benchmark.py",
        template_key="mythology",
    )

    with SessionLocal() as db:
        existing = get_project(project_key, db=db)
        if existing is not None and existing.editable:
            delete_managed_project(db, project_key)

        created = create_managed_project(db, mutation)
        assert created.source_kind == "managed"
        assert created.editable is True
        assert created.template_key == "mythology"

        updated = update_managed_project(
            db,
            project_key,
            ProjectMutation(
                **{
                    **mutation.__dict__,
                    "name": "Updated Managed Project",
                    "metric_direction": MetricDirection.MINIMIZE,
                    "metric_name": "loss",
                }
            ),
        )
        assert updated.name == "Updated Managed Project"
        assert updated.metric_direction is MetricDirection.MINIMIZE
        assert get_project(project_key, db=db) is not None

        delete_managed_project(db, project_key)
        assert get_project(project_key, db=db) is None


def test_managed_project_bootstrap_generates_starter_files() -> None:
    init_db()
    project_key = "test-bootstrap-project"
    mutation = ProjectMutation(
        key=project_key,
        name="Bootstrap Project",
        description="Managed project used to verify starter generation.",
        mutable_artifact=f"projects/{project_key}/train.py",
        autonomous_mutable_artifacts=(f"projects/{project_key}/train.py",),
        setup_artifacts=(
            f"projects/{project_key}/prepare.py",
            f"projects/{project_key}/program.md",
            f"projects/{project_key}/run_benchmark.py",
        ),
        dependency_artifacts=("pyproject.toml", "uv.lock"),
        metric_name="score",
        metric_direction=MetricDirection.MAXIMIZE,
        min_budget_seconds=30,
        default_budget_seconds=60,
        max_budget_seconds=120,
        runner_key="python-benchmark",
        execution_entrypoint=f"projects/{project_key}/run_benchmark.py",
        template_key="helpdesk",
    )

    with SessionLocal() as db:
        existing = get_project(project_key, db=db)
        if existing is not None and existing.editable:
            delete_managed_project(db, project_key)

        created = create_managed_project(db, mutation)
        result = bootstrap_project_workspace(created, overwrite=True)

        mutable_path = ROOT_DIR / created.mutable_artifact
        entrypoint_path = ROOT_DIR / created.execution_entrypoint
        program_path = ROOT_DIR / f"projects/{project_key}/program.md"

        assert mutable_path.exists()
        assert entrypoint_path.exists()
        assert program_path.exists()
        assert result.project_key == project_key
        assert "def evaluate_metric()" in mutable_path.read_text(encoding="utf-8")
        assert '"status": "succeeded"' in entrypoint_path.read_text(encoding="utf-8")
        assert created.metric_name in program_path.read_text(encoding="utf-8")

        delete_managed_project(db, project_key)
        shutil.rmtree(ROOT_DIR / f"projects/{project_key}", ignore_errors=True)
