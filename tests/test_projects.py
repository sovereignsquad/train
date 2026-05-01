import json
import subprocess

from autotrain_core.db import SessionLocal, init_db
from autotrain_core.models import MetricDirection
from autotrain_core.projects import (
    ProjectMutation,
    create_managed_project,
    delete_managed_project,
    get_project,
    list_projects,
    update_managed_project,
)
from autotrain_core.ratchet import is_better_metric


def test_project_registry_contains_second_project() -> None:
    keys = {project.key for project in list_projects()}
    assert "mythology" in keys
    assert "helpdesk" in keys

    helpdesk = get_project("helpdesk")
    assert helpdesk is not None
    assert helpdesk.metric_name == "macro_f1"
    assert helpdesk.metric_direction.value == "maximize"
    assert helpdesk.mutable_artifact == "projects/helpdesk/train.py"


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
