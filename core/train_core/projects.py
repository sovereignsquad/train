from dataclasses import dataclass
import json
from pathlib import Path
import sys
from textwrap import dedent

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from train_core.config import ROOT_DIR
from train_core.db import SessionLocal
from train_core.models import ManagedProject, MetricDirection


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


@dataclass(frozen=True)
class ProjectBootstrapResult:
    project_key: str
    project_root: str
    created_files: tuple[str, ...]
    overwritten_files: tuple[str, ...]
    skipped_files: tuple[str, ...]


REFERENCE_PROJECTS: dict[str, ProjectDefinition] = {
    "trinity_frontier": ProjectDefinition(
        key="trinity_frontier",
        name="Trinity Frontier Benchmark",
        description=(
            "Bounded Trinity runtime component benchmark for train. It optimizes the frontier "
            "ranking heuristic without absorbing Trinity runtime ownership."
        ),
        mutable_artifact="projects/trinity_frontier/train.py",
        autonomous_mutable_artifacts=("projects/trinity_frontier/train.py",),
        setup_artifacts=(
            "projects/trinity_frontier/prepare.py",
            "projects/trinity_frontier/program.md",
            "projects/trinity_frontier/run_benchmark.py",
            "projects/trinity_frontier/eval_fixture.json",
        ),
        dependency_artifacts=("pyproject.toml", "uv.lock"),
        metric_name="ranking_score",
        metric_direction=MetricDirection.MAXIMIZE,
        min_budget_seconds=30,
        default_budget_seconds=60,
        max_budget_seconds=180,
        runner_key="python-benchmark",
        execution_entrypoint="projects/trinity_frontier/run_benchmark.py",
        source_kind="reference",
        editable=False,
        deletable=False,
        template_key="trinity_frontier",
    ),
    "reply": ProjectDefinition(
        key="reply",
        name="Reply Draft Benchmark",
        description=(
            "Starter Trinity-style reference project for train using local reply-drafting "
            "fixtures and a deterministic maximize metric."
        ),
        mutable_artifact="projects/reply/train.py",
        autonomous_mutable_artifacts=("projects/reply/train.py",),
        setup_artifacts=(
            "projects/reply/prepare.py",
            "projects/reply/program.md",
            "projects/reply/run_benchmark.py",
            "projects/reply/eval_fixture.json",
        ),
        dependency_artifacts=("pyproject.toml", "uv.lock"),
        metric_name="draft_score",
        metric_direction=MetricDirection.MAXIMIZE,
        min_budget_seconds=30,
        default_budget_seconds=60,
        max_budget_seconds=180,
        runner_key="python-benchmark",
        execution_entrypoint="projects/reply/run_benchmark.py",
        source_kind="reference",
        editable=False,
        deletable=False,
        template_key="reply",
    ),
    "helpdesk": ProjectDefinition(
        key="helpdesk",
        name="Helpdesk Intent Benchmark",
        description=(
            "Second reference benchmark for train using deterministic helpdesk intent "
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
            "First reference benchmark for train using mythology and folktales as "
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
    return ROOT_DIR / Path(project.mutable_artifact).parent


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


def bootstrap_project_workspace(
    project: ProjectDefinition,
    *,
    overwrite: bool = False,
) -> ProjectBootstrapResult:
    project_root = get_project_root(project)
    project_root.mkdir(parents=True, exist_ok=True)

    created_files: list[str] = []
    overwritten_files: list[str] = []
    skipped_files: list[str] = []

    for relative_path, content in _build_bootstrap_file_payloads(project).items():
        absolute_path = ROOT_DIR / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)

        if absolute_path.exists():
            if overwrite:
                absolute_path.write_text(content, encoding="utf-8")
                overwritten_files.append(relative_path)
            else:
                skipped_files.append(relative_path)
            continue

        absolute_path.write_text(content, encoding="utf-8")
        created_files.append(relative_path)

    return ProjectBootstrapResult(
        project_key=project.key,
        project_root=str(project_root),
        created_files=tuple(created_files),
        overwritten_files=tuple(overwritten_files),
        skipped_files=tuple(skipped_files),
    )


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
    _validate_project_paths(mutation)


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


def _validate_project_paths(mutation: ProjectMutation) -> None:
    project_dir = Path(mutation.mutable_artifact).parent.as_posix()
    _require_project_path(mutation.mutable_artifact, "Mutable artifact")
    _require_project_path(mutation.execution_entrypoint, "Execution entrypoint")

    if Path(mutation.execution_entrypoint).parent.as_posix() != project_dir:
        raise ProjectMutationError("Execution entrypoint must live beside the mutable artifact.")

    for path in mutation.autonomous_mutable_artifacts:
        _require_project_path(path, "Autonomous mutable artifact")
        if Path(path).parent.as_posix() != project_dir:
            raise ProjectMutationError(
                "Autonomous mutable artifacts must live beside the primary mutable artifact."
            )

    for path in mutation.setup_artifacts:
        _require_project_path(path, "Setup artifact")
        if Path(path).parent.as_posix() != project_dir:
            raise ProjectMutationError("Setup artifacts must live beside the primary mutable artifact.")


def _require_project_path(path: str, label: str) -> None:
    if not Path(path).as_posix().startswith("projects/"):
        raise ProjectMutationError(f"{label} must live under the projects/ workspace.")


def _build_bootstrap_file_payloads(project: ProjectDefinition) -> dict[str, str]:
    module_name = Path(project.mutable_artifact).stem
    metric_seed = "0.0" if project.metric_direction is MetricDirection.MAXIMIZE else "1.0"
    payloads: dict[str, str] = {
        project.mutable_artifact: _starter_train_module(project, metric_seed),
        project.execution_entrypoint: _starter_benchmark_entrypoint(project, module_name),
    }

    for setup_artifact in project.setup_artifacts:
        name = Path(setup_artifact).name
        if setup_artifact == project.execution_entrypoint:
            continue
        if name == "prepare.py":
            payloads[setup_artifact] = _starter_prepare_module(project)
        elif name == "program.md":
            payloads[setup_artifact] = _starter_program_doc(project)
        else:
            payloads[setup_artifact] = _starter_placeholder(project, setup_artifact)
    return payloads


def _starter_train_module(project: ProjectDefinition, metric_seed: str) -> str:
    comparison_hint = (
        "Increase the returned score when your experiment improves."
        if project.metric_direction is MetricDirection.MAXIMIZE
        else "Decrease the returned score when your experiment improves."
    )
    return dedent(
        f'''\
        """Starter mutable artifact for {project.key}."""


        def evaluate_metric() -> float:
            """
            Return one deterministic scalar score for the project.

            Implement for this project:
            - real evaluation logic
            - deterministic output for comparable runs
            - {comparison_hint}
            """

            return {metric_seed}
        '''
    )


def _starter_prepare_module(project: ProjectDefinition) -> str:
    return dedent(
        f'''\
        """Setup helpers for {project.key}."""


        def ensure_prepared() -> None:
            """
            Prepare local resources for the benchmark.

            Setup checklist:
            - download or generate local data if needed
            - keep setup deterministic and idempotent
            """

            return None
        '''
    )


def _starter_benchmark_entrypoint(project: ProjectDefinition, module_name: str) -> str:
    return dedent(
        f'''\
        from __future__ import annotations

        import argparse
        import importlib.util
        import json
        from pathlib import Path

        from prepare import ensure_prepared


        def _load_mutable_module():
            module_path = Path(__file__).with_name("{module_name}.py")
            spec = importlib.util.spec_from_file_location("{module_name}", module_path)
            if spec is None or spec.loader is None:
                raise RuntimeError(f"Unable to load mutable module from {{module_path}}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module


        def run_benchmark() -> dict[str, object]:
            ensure_prepared()
            module = _load_mutable_module()
            metric_value = float(module.evaluate_metric())
            return {{
                "status": "succeeded",
                "metric_value": round(metric_value, 6),
                "result_summary": (
                    "Starter benchmark completed for {project.key}. Replace the placeholder "
                    "logic with a real deterministic evaluation."
                ),
                "error_message": None,
            }}


        def main() -> None:
            parser = argparse.ArgumentParser()
            parser.add_argument("--budget-seconds", type=int, required=True)
            parser.add_argument("--run-id", type=int, required=True)
            parser.parse_args()
            print(json.dumps(run_benchmark()))


        if __name__ == "__main__":
            main()
        '''
    )


def _starter_program_doc(project: ProjectDefinition) -> str:
    comparison_hint = "higher is better" if project.metric_direction is MetricDirection.MAXIMIZE else "lower is better"
    return dedent(
        f"""\
        # {project.name}

        This is a generated starter project for `train`.

        Purpose:

        - define one controlled mutable artifact
        - define one bounded execution entrypoint
        - emit one machine-readable metric
        - stay compatible with the git ratchet and run ledger

        Current contract:

        - mutable artifact: `{project.mutable_artifact}`
        - entrypoint: `{project.execution_entrypoint}`
        - metric: `{project.metric_name}`
        - direction: {comparison_hint}

        Rules:

        1. Only modify the declared mutable artifact during autonomous runs.
        2. Keep setup and benchmark files deterministic.
        3. Replace the placeholder logic with a real local evaluation before trusting results.
        """
    )


def _starter_placeholder(project: ProjectDefinition, path: str) -> str:
    return dedent(
        f"""\
        Placeholder file for `{project.key}`.

        Generated for: `{path}`
        """
    )
