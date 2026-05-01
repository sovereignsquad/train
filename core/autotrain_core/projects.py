from dataclasses import dataclass
import json
from pathlib import Path
import sys

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from autotrain_core.config import ROOT_DIR
from autotrain_core.db import SessionLocal
from autotrain_core.models import ManagedProject, MetricDirection


@dataclass(frozen=True)
class ProjectDefinition:
    key: str
    name: str
    description: str
    mutable_artifact: str
    autonomous_mutable_artifacts: tuple[str, ...]
    setup_artifacts: tuple[str, ...]
    dependency_artifacts: tuple[str, ...]
    metric_name: str
    metric_direction: MetricDirection
    min_budget_seconds: int
    default_budget_seconds: int
    max_budget_seconds: int
    runner_key: str
    execution_entrypoint: str
    source_kind: str
    editable: bool
    deletable: bool
    template_key: str | None


@dataclass(frozen=True)
class ProjectMutation:
    key: str
    name: str
    description: str
    mutable_artifact: str
    autonomous_mutable_artifacts: tuple[str, ...]
    setup_artifacts: tuple[str, ...]
    dependency_artifacts: tuple[str, ...]
    metric_name: str
    metric_direction: MetricDirection
    min_budget_seconds: int
    default_budget_seconds: int
    max_budget_seconds: int
    runner_key: str
    execution_entrypoint: str
    template_key: str | None = None


class ProjectMutationError(ValueError):
    """Raised when a managed project payload is invalid."""


REFERENCE_PROJECTS: dict[str, ProjectDefinition] = {
    "helpdesk": ProjectDefinition(
        key="helpdesk",
        name="Helpdesk Intent Benchmark",
        description=(
            "Second reference benchmark for autotrain using deterministic helpdesk intent "
            "classification to validate a maximize-metric project shape."
        ),
        mutable_artifact="projects/helpdesk/train.py",
        autonomous_mutable_artifacts=("projects/helpdesk/train.py",),
        setup_artifacts=(
            "projects/helpdesk/prepare.py",
            "projects/helpdesk/program.md",
            "projects/helpdesk/run_benchmark.py",
        ),
        dependency_artifacts=("pyproject.toml", "uv.lock"),
        metric_name="macro_f1",
        metric_direction=MetricDirection.MAXIMIZE,
        min_budget_seconds=30,
        default_budget_seconds=60,
        max_budget_seconds=180,
        runner_key="python-benchmark",
        execution_entrypoint="projects/helpdesk/run_benchmark.py",
        source_kind="reference",
        editable=False,
        deletable=False,
        template_key="helpdesk",
    ),
    "mythology": ProjectDefinition(
        key="mythology",
        name="Mythology Benchmark",
        description=(
            "First reference benchmark for autotrain using mythology and folktales as "
            "the proving ground for the general-purpose platform contract."
        ),
        mutable_artifact="projects/mythology/train.py",
        autonomous_mutable_artifacts=("projects/mythology/train.py",),
        setup_artifacts=(
            "projects/mythology/prepare.py",
            "projects/mythology/program.md",
            "projects/mythology/run_benchmark.py",
        ),
        dependency_artifacts=("pyproject.toml", "uv.lock"),
        metric_name="val_bpb",
        metric_direction=MetricDirection.MINIMIZE,
        min_budget_seconds=60,
        default_budget_seconds=300,
        max_budget_seconds=300,
        runner_key="python-benchmark",
        execution_entrypoint="projects/mythology/run_benchmark.py",
        source_kind="reference",
        editable=False,
        deletable=False,
        template_key="mythology",
    ),
}


def list_reference_projects() -> list[ProjectDefinition]:
    return list(REFERENCE_PROJECTS.values())


def list_projects(db: Session | None = None) -> list[ProjectDefinition]:
    if db is None:
        with SessionLocal() as owned_session:
            return _list_projects(owned_session)
    return _list_projects(db)


def list_managed_projects(db: Session) -> list[ProjectDefinition]:
    if not _managed_projects_table_exists(db):
        return []
    rows = db.query(ManagedProject).order_by(ManagedProject.name.asc(), ManagedProject.key.asc()).all()
    return [_managed_row_to_definition(row) for row in rows]


def get_project(project_key: str, db: Session | None = None) -> ProjectDefinition | None:
    if project_key in REFERENCE_PROJECTS:
        return REFERENCE_PROJECTS[project_key]

    if db is None:
        with SessionLocal() as owned_session:
            return _get_managed_project(project_key, owned_session)
    return _get_managed_project(project_key, db)


def create_managed_project(db: Session, mutation: ProjectMutation) -> ProjectDefinition:
    _require_managed_projects_table(db)
    _validate_project_mutation(mutation)
    if mutation.key in REFERENCE_PROJECTS:
        raise ProjectMutationError(
            f"Project key '{mutation.key}' is reserved by a reference template."
        )
    if db.get(ManagedProject, mutation.key) is not None:
        raise ProjectMutationError(f"Project key '{mutation.key}' already exists.")

    row = ManagedProject(
        key=mutation.key,
        name=mutation.name,
        description=mutation.description,
        mutable_artifact=mutation.mutable_artifact,
        autonomous_mutable_artifacts_json=_dumps_items(mutation.autonomous_mutable_artifacts),
        setup_artifacts_json=_dumps_items(mutation.setup_artifacts),
        dependency_artifacts_json=_dumps_items(mutation.dependency_artifacts),
        metric_name=mutation.metric_name,
        metric_direction=mutation.metric_direction,
        min_budget_seconds=mutation.min_budget_seconds,
        default_budget_seconds=mutation.default_budget_seconds,
        max_budget_seconds=mutation.max_budget_seconds,
        runner_key=mutation.runner_key,
        execution_entrypoint=mutation.execution_entrypoint,
        template_key=mutation.template_key,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _managed_row_to_definition(row)


def update_managed_project(db: Session, project_key: str, mutation: ProjectMutation) -> ProjectDefinition:
    _require_managed_projects_table(db)
    if project_key in REFERENCE_PROJECTS:
        raise ProjectMutationError("Reference templates are read-only and cannot be updated.")
    if mutation.key != project_key:
        raise ProjectMutationError("Project key cannot be changed once created.")

    _validate_project_mutation(mutation)
    row = db.get(ManagedProject, project_key)
    if row is None:
        raise ProjectMutationError(f"Managed project '{project_key}' was not found.")

    row.name = mutation.name
    row.description = mutation.description
    row.mutable_artifact = mutation.mutable_artifact
    row.autonomous_mutable_artifacts_json = _dumps_items(mutation.autonomous_mutable_artifacts)
    row.setup_artifacts_json = _dumps_items(mutation.setup_artifacts)
    row.dependency_artifacts_json = _dumps_items(mutation.dependency_artifacts)
    row.metric_name = mutation.metric_name
    row.metric_direction = mutation.metric_direction
    row.min_budget_seconds = mutation.min_budget_seconds
    row.default_budget_seconds = mutation.default_budget_seconds
    row.max_budget_seconds = mutation.max_budget_seconds
    row.runner_key = mutation.runner_key
    row.execution_entrypoint = mutation.execution_entrypoint
    row.template_key = mutation.template_key
    db.add(row)
    db.commit()
    db.refresh(row)
    return _managed_row_to_definition(row)


def delete_managed_project(db: Session, project_key: str) -> None:
    _require_managed_projects_table(db)
    if project_key in REFERENCE_PROJECTS:
        raise ProjectMutationError("Reference templates are read-only and cannot be deleted.")

    row = db.get(ManagedProject, project_key)
    if row is None:
        raise ProjectMutationError(f"Managed project '{project_key}' was not found.")

    db.delete(row)
    db.commit()


def get_project_root(project: ProjectDefinition) -> Path:
    return ROOT_DIR / "projects" / project.key


def build_run_command(project: ProjectDefinition, *, budget_seconds: int, run_id: int) -> list[str]:
    entrypoint = ROOT_DIR / project.execution_entrypoint
    return [
        sys.executable,
        str(entrypoint),
        "--budget-seconds",
        str(budget_seconds),
        "--run-id",
        str(run_id),
    ]


def _list_projects(db: Session) -> list[ProjectDefinition]:
    projects = [*list_reference_projects(), *list_managed_projects(db)]
    return sorted(projects, key=lambda project: (project.source_kind != "managed", project.name.lower(), project.key))


def _get_managed_project(project_key: str, db: Session) -> ProjectDefinition | None:
    if not _managed_projects_table_exists(db):
        return None
    row = db.get(ManagedProject, project_key)
    if row is None:
        return None
    return _managed_row_to_definition(row)


def _managed_row_to_definition(row: ManagedProject) -> ProjectDefinition:
    return ProjectDefinition(
        key=row.key,
        name=row.name,
        description=row.description,
        mutable_artifact=row.mutable_artifact,
        autonomous_mutable_artifacts=_loads_items(row.autonomous_mutable_artifacts_json),
        setup_artifacts=_loads_items(row.setup_artifacts_json),
        dependency_artifacts=_loads_items(row.dependency_artifacts_json),
        metric_name=row.metric_name,
        metric_direction=row.metric_direction,
        min_budget_seconds=row.min_budget_seconds,
        default_budget_seconds=row.default_budget_seconds,
        max_budget_seconds=row.max_budget_seconds,
        runner_key=row.runner_key,
        execution_entrypoint=row.execution_entrypoint,
        source_kind="managed",
        editable=True,
        deletable=True,
        template_key=row.template_key,
    )


def _validate_project_mutation(mutation: ProjectMutation) -> None:
    if mutation.min_budget_seconds > mutation.default_budget_seconds:
        raise ProjectMutationError("Default budget must be greater than or equal to min budget.")
    if mutation.default_budget_seconds > mutation.max_budget_seconds:
        raise ProjectMutationError("Default budget must be less than or equal to max budget.")
    if not mutation.autonomous_mutable_artifacts:
        raise ProjectMutationError("At least one autonomous mutable artifact is required.")
    if mutation.mutable_artifact not in mutation.autonomous_mutable_artifacts:
        raise ProjectMutationError(
            "The primary mutable artifact must appear in autonomous mutable artifacts."
        )
    if not mutation.setup_artifacts:
        raise ProjectMutationError("At least one setup artifact is required.")
    if not mutation.dependency_artifacts:
        raise ProjectMutationError("At least one dependency artifact is required.")


def _dumps_items(items: tuple[str, ...]) -> str:
    return json.dumps(list(items))


def _loads_items(payload: str) -> tuple[str, ...]:
    values = json.loads(payload)
    if not isinstance(values, list):
        raise ProjectMutationError("Stored project artifact payload is invalid.")
    return tuple(str(value) for value in values)


def _managed_projects_table_exists(db: Session) -> bool:
    return "managed_projects" in set(inspect(db.get_bind()).get_table_names())


def _require_managed_projects_table(db: Session) -> None:
    if not _managed_projects_table_exists(db):
        raise ProjectMutationError("Managed project storage is not initialized. Start the API once to run migrations.")
