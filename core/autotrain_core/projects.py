from dataclasses import dataclass
from pathlib import Path
import sys

from autotrain_core.config import ROOT_DIR
from autotrain_core.models import MetricDirection


@dataclass(frozen=True)
class ProjectDefinition:
    key: str
    name: str
    description: str
    mutable_artifact: str
    metric_name: str
    metric_direction: MetricDirection
    default_budget_seconds: int
    runner_key: str
    execution_entrypoint: str


PROJECTS: dict[str, ProjectDefinition] = {
    "mythology": ProjectDefinition(
        key="mythology",
        name="Mythology Benchmark",
        description=(
            "First reference benchmark for autotrain using mythology and folktales as "
            "the proving ground for the general-purpose platform contract."
        ),
        mutable_artifact="projects/mythology/train.py",
        metric_name="val_bpb",
        metric_direction=MetricDirection.MINIMIZE,
        default_budget_seconds=300,
        runner_key="python-benchmark",
        execution_entrypoint="projects/mythology/run_benchmark.py",
    )
}


def list_projects() -> list[ProjectDefinition]:
    return list(PROJECTS.values())


def get_project(project_key: str) -> ProjectDefinition | None:
    return PROJECTS.get(project_key)


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
