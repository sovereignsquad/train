from dataclasses import dataclass

from autotrain_core.projects import ProjectDefinition


class GuardrailError(ValueError):
    """Raised when an autonomous run leaves the allowed workspace envelope."""


@dataclass(frozen=True)
class GuardrailReport:
    allowed_paths: tuple[str, ...]
    setup_paths: tuple[str, ...]
    dependency_paths: tuple[str, ...]
    unauthorized_paths: tuple[str, ...]

    @property
    def has_violations(self) -> bool:
        return bool(self.setup_paths or self.dependency_paths or self.unauthorized_paths)


def validate_run_budget(project: ProjectDefinition, budget_seconds: int) -> None:
    if budget_seconds < project.min_budget_seconds or budget_seconds > project.max_budget_seconds:
        raise GuardrailError(
            f"Budget {budget_seconds}s is outside the allowed range for project "
            f"'{project.key}' ({project.min_budget_seconds}s to {project.max_budget_seconds}s)."
        )


def classify_changed_paths(project: ProjectDefinition, changed_paths: list[str]) -> GuardrailReport:
    allowed_paths: list[str] = []
    setup_paths: list[str] = []
    dependency_paths: list[str] = []
    unauthorized_paths: list[str] = []

    allowed_set = set(project.autonomous_mutable_artifacts)
    setup_set = set(project.setup_artifacts)
    dependency_set = set(project.dependency_artifacts)

    for path in changed_paths:
        if path in allowed_set:
            allowed_paths.append(path)
            continue
        if path in setup_set:
            setup_paths.append(path)
            continue
        if path in dependency_set:
            dependency_paths.append(path)
            continue
        unauthorized_paths.append(path)

    return GuardrailReport(
        allowed_paths=tuple(sorted(set(allowed_paths))),
        setup_paths=tuple(sorted(set(setup_paths))),
        dependency_paths=tuple(sorted(set(dependency_paths))),
        unauthorized_paths=tuple(sorted(set(unauthorized_paths))),
    )


def validate_autonomous_workspace(project: ProjectDefinition, changed_paths: list[str]) -> GuardrailReport:
    report = classify_changed_paths(project, changed_paths)
    if not report.has_violations:
        return report

    problems: list[str] = []
    if report.setup_paths:
        problems.append("setup artifacts changed: " + ", ".join(report.setup_paths))
    if report.dependency_paths:
        problems.append("dependency artifacts changed: " + ", ".join(report.dependency_paths))
    if report.unauthorized_paths:
        problems.append("unauthorized artifacts changed: " + ", ".join(report.unauthorized_paths))

    raise GuardrailError("Autonomous workspace guardrail violation: " + " | ".join(problems))
