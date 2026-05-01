from autotrain_core.guardrails import GuardrailError, classify_changed_paths, validate_run_budget, validate_autonomous_workspace
from autotrain_core.projects import get_project


def test_budget_bounds_are_enforced() -> None:
    project = get_project("mythology")
    assert project is not None

    validate_run_budget(project, 60)
    validate_run_budget(project, 300)

    try:
        validate_run_budget(project, 30)
    except GuardrailError as exc:
        assert "outside the allowed range" in str(exc)
    else:
        raise AssertionError("Expected low budget to fail guardrails")


def test_workspace_classification_distinguishes_dependency_and_setup_paths() -> None:
    project = get_project("mythology")
    assert project is not None

    report = classify_changed_paths(
        project,
        [
            "projects/mythology/train.py",
            "projects/mythology/program.md",
            "pyproject.toml",
            "scripts/run_vibe.py",
        ],
    )

    assert report.allowed_paths == ("projects/mythology/train.py",)
    assert report.setup_paths == ("projects/mythology/program.md",)
    assert report.dependency_paths == ("pyproject.toml",)
    assert report.unauthorized_paths == ("scripts/run_vibe.py",)


def test_workspace_guardrails_fail_closed() -> None:
    project = get_project("mythology")
    assert project is not None

    try:
        validate_autonomous_workspace(project, ["projects/mythology/program.md"])
    except GuardrailError as exc:
        assert "setup artifacts changed" in str(exc)
    else:
        raise AssertionError("Expected setup artifact mutation to fail guardrails")
