from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from train_core.cli import main as train_cli_main
from train_core.health import (
    HealthCheckResult,
    HealthReport,
    TrainingReadinessError,
    assert_training_lane_ready,
    check_training_lane_readiness,
)
from train_api.main import get_doctor_report
from train_core.schemas import HealthReportRead


def test_check_training_lane_readiness_warns_when_mlx_lm_missing(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr("platform.machine", lambda: "arm64")
    monkeypatch.setattr("importlib.util.find_spec", lambda name: None)
    monkeypatch.setattr("train_core.config.settings.train_models_root", str(tmp_path))

    check = check_training_lane_readiness(required=False)

    assert check.status == "warn"
    assert "mlx_lm is not installed" in " ".join(check.details["problems"])


def test_check_training_lane_readiness_fails_for_missing_local_model(monkeypatch, tmp_path: Path) -> None:
    @dataclass(frozen=True)
    class FakeSpec:
        ref: str = "reply_sft@2026-05-13.1"
        base_model_source_kind: str = "local-path"
        base_model_ref: str = "llms/reply/model"
        output_dir: str = str(tmp_path / "output")

    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr("platform.machine", lambda: "arm64")
    monkeypatch.setattr("importlib.util.find_spec", lambda name: object())
    monkeypatch.setattr("train_core.config.settings.train_models_root", str(tmp_path / "models-root"))

    check = check_training_lane_readiness(required=True, spec=FakeSpec())

    assert check.status == "fail"
    assert any("does not exist" in item for item in check.details["problems"])


def test_assert_training_lane_ready_raises(monkeypatch, tmp_path: Path) -> None:
    @dataclass(frozen=True)
    class FakeSpec:
        ref: str = "reply_sft@2026-05-13.1"
        base_model_source_kind: str = "huggingface"
        base_model_ref: str = "mlx-community/Llama-3.2-3B-Instruct-4bit"
        output_dir: str = str(tmp_path / "missing-output")

    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr("platform.machine", lambda: "arm64")
    monkeypatch.setattr("importlib.util.find_spec", lambda name: object())

    with pytest.raises(TrainingReadinessError, match="output_dir"):
        assert_training_lane_ready(spec=FakeSpec())


def test_doctor_cli_uses_summary_renderer(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "train_core.cli.build_doctor_report",
        lambda **_: HealthReport(
            workflow="default",
            generated_at="2026-05-19T00:00:00Z",
            overall_status="pass",
            ok=True,
            warning_count=0,
            failure_count=0,
            checks=(
                HealthCheckResult(
                    key="train-api",
                    status="pass",
                    summary="train-api responded successfully.",
                    details={"base_url": "http://127.0.0.1:8000"},
                ),
            ),
        ),
    )

    exit_code = train_cli_main(["doctor", "--output-format", "summary"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "overall_status: pass" in output
    assert "train-api: pass" in output


def test_doctor_route_returns_health_report(monkeypatch) -> None:
    monkeypatch.setattr(
        "train_api.main.build_doctor_report",
        lambda **_: HealthReport(
            workflow="training",
            generated_at="2026-05-19T00:00:00Z",
            overall_status="warn",
            ok=False,
            warning_count=1,
            failure_count=0,
            checks=(
                HealthCheckResult(
                    key="offline-training",
                    status="warn",
                    summary="mlx_lm is not installed.",
                    details={"problem_count": 1},
                    remediation="Install mlx-lm.",
                ),
            ),
        ),
    )

    result = get_doctor_report(workflow="training")

    assert isinstance(result, HealthReportRead)
    assert result.workflow == "training"
    assert result.overall_status == "warn"
    assert result.checks[0].key == "offline-training"
