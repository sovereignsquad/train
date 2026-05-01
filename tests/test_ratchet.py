from __future__ import annotations

from types import SimpleNamespace

import pytest

from train_core.guardrails import GuardrailError, GuardrailReport
from train_core.models import GitAction, RatchetDecision, RunRecord
from train_core.ratchet import RatchetError, _apply_git_mutation


def test_apply_git_mutation_commits_all_changed_allowed_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    run = RunRecord(
        id=7,
        project_key="multi-artifact",
        title="Candidate run",
        ratchet_decision=RatchetDecision.ACCEPTED,
        mutable_artifact="projects/multi/train.py",
    )
    report = GuardrailReport(
        allowed_paths=("projects/multi/config.json", "projects/multi/train.py"),
        setup_paths=(),
        dependency_paths=(),
        unauthorized_paths=(),
    )
    committed: list[tuple[tuple[str, ...], int]] = []

    monkeypatch.setattr(
        "train_core.ratchet.get_changed_paths",
        lambda: ["projects/multi/train.py", "projects/multi/config.json"],
    )
    monkeypatch.setattr(
        "train_core.ratchet.get_project",
        lambda _: SimpleNamespace(autonomous_mutable_artifacts=report.allowed_paths),
    )
    monkeypatch.setattr("train_core.ratchet.validate_autonomous_workspace", lambda *_: report)
    monkeypatch.setattr(
        "train_core.ratchet.commit_mutable_artifacts",
        lambda paths, candidate_run: committed.append((paths, candidate_run.id)),
    )

    _apply_git_mutation(run)

    assert run.git_action == GitAction.COMMITTED
    assert committed == [(
        ("projects/multi/config.json", "projects/multi/train.py"),
        7,
    )]


def test_apply_git_mutation_restores_all_changed_allowed_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    run = RunRecord(
        id=8,
        project_key="multi-artifact",
        title="Rejected run",
        ratchet_decision=RatchetDecision.REJECTED,
        mutable_artifact="projects/multi/train.py",
    )
    report = GuardrailReport(
        allowed_paths=("projects/multi/config.json", "projects/multi/train.py"),
        setup_paths=(),
        dependency_paths=(),
        unauthorized_paths=(),
    )
    restored: list[tuple[str, ...]] = []

    monkeypatch.setattr(
        "train_core.ratchet.get_changed_paths",
        lambda: ["projects/multi/train.py", "projects/multi/config.json"],
    )
    monkeypatch.setattr(
        "train_core.ratchet.get_project",
        lambda _: SimpleNamespace(autonomous_mutable_artifacts=report.allowed_paths),
    )
    monkeypatch.setattr("train_core.ratchet.validate_autonomous_workspace", lambda *_: report)
    monkeypatch.setattr(
        "train_core.ratchet.restore_mutable_artifacts",
        lambda paths: restored.append(paths),
    )

    _apply_git_mutation(run)

    assert run.git_action == GitAction.RESTORED
    assert restored == [("projects/multi/config.json", "projects/multi/train.py")]


def test_apply_git_mutation_blocks_unauthorized_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    run = RunRecord(
        id=9,
        project_key="multi-artifact",
        title="Blocked run",
        ratchet_decision=RatchetDecision.ACCEPTED,
        mutable_artifact="projects/multi/train.py",
    )

    monkeypatch.setattr(
        "train_core.ratchet.get_changed_paths",
        lambda: ["projects/multi/train.py", "README.md"],
    )
    monkeypatch.setattr(
        "train_core.ratchet.get_project",
        lambda _: SimpleNamespace(
            autonomous_mutable_artifacts=("projects/multi/train.py", "projects/multi/config.json")
        ),
    )

    def raise_guardrail(*_args: object, **_kwargs: object) -> GuardrailReport:
        raise GuardrailError("Autonomous workspace guardrail violation: unauthorized artifacts changed: README.md")

    monkeypatch.setattr("train_core.ratchet.validate_autonomous_workspace", raise_guardrail)

    with pytest.raises(RatchetError, match="unauthorized artifacts changed: README.md"):
        _apply_git_mutation(run)

    assert run.git_action == GitAction.BLOCKED
