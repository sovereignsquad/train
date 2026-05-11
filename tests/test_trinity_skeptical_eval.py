from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from train_api.main import build_trinity_skeptical_eval
from train_core.cli import main as train_cli_main
from train_core.comparison import StandardComparisonRow, build_standard_comparison_report
from train_core.models import MetricDirection
from train_core.schemas import TrinitySkepticalEvalRequest
from train_core.trinity_skeptical_eval import build_skeptical_eval_report


def _write_comparison_report(
    path: Path,
    *,
    sample_count: int = 6,
    incumbent_score: float | None = 0.82,
    candidate_score: float | None = 0.87,
    baseline_score: float | None = 0.8,
    incumbent_status: str = "evaluated",
) -> Path:
    rows = []
    if baseline_score is not None:
        rows.append(
            StandardComparisonRow(
                label="baseline",
                artifact_key="retrieval_selection_policy",
                version="baseline.v1",
                score=baseline_score,
                status="evaluated",
                notes="fixture baseline",
            )
        )
    rows.append(
        StandardComparisonRow(
            label="incumbent",
            artifact_key="retrieval_selection_policy",
            version="incumbent.v1",
            score=incumbent_score,
            status=incumbent_status,
            notes="fixture incumbent",
        )
    )
    rows.append(
        StandardComparisonRow(
            label="candidate",
            artifact_key="retrieval_selection_policy",
            version="candidate.v1",
            score=candidate_score,
            status="evaluated" if candidate_score is not None else "metadata_only",
            notes="fixture candidate",
        )
    )
    report = build_standard_comparison_report(
        report_id="retrieval.candidate.v1.comparison",
        generated_at=datetime(2026, 5, 11, 9, 0, tzinfo=UTC),
        evaluation_mode="fixed_replay_corpus",
        metric_name="retrieval_selection_policy_fit",
        metric_direction=MetricDirection.MAXIMIZE,
        sample_count=sample_count,
        corpus_fingerprint="abc123",
        rows=rows,
        summary="Fixture comparison.",
    )
    path.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
    return path


def test_build_skeptical_eval_report_holds_when_incumbent_is_missing(tmp_path: Path) -> None:
    comparison_path = _write_comparison_report(
        tmp_path / "comparison.json",
        incumbent_score=None,
        incumbent_status="metadata_only",
    )
    output_path = tmp_path / "skeptical.json"

    result = build_skeptical_eval_report(
        component_key="memory_retriever",
        artifact_family="retrieval_selection_policy",
        proposal_artifact_version="candidate.v1",
        proposal_ref="artifacts/proposals/candidate.v1.json",
        comparison_report_file=comparison_path,
        review_scope_kind="company",
        review_scope_value="company-1",
        skeptical_eval_output_path=output_path,
        hidden_confounds=("incumbent replay unavailable",),
    )

    report = result.skeptical_eval_report
    assert result.skeptical_eval_output_path == str(output_path)
    assert report["promotion_readiness"] == "NOT_PROMOTION_READY"
    assert report["review_outcome"] == "HOLD_FOR_MORE_EVIDENCE"
    assert any(item["reason_code"] == "INCOMPLETE_INCUMBENT_EVIDENCE" for item in report["rejection_evidence"])
    assert report["minority_report"]["hidden_confounds"] == ["incumbent replay unavailable"]


def test_build_skeptical_eval_report_rejects_regression(tmp_path: Path) -> None:
    comparison_path = _write_comparison_report(
        tmp_path / "comparison.json",
        incumbent_score=0.84,
        candidate_score=0.81,
    )

    result = build_skeptical_eval_report(
        component_key="memory_retriever",
        artifact_family="retrieval_selection_policy",
        proposal_artifact_version="candidate.v1",
        proposal_ref="artifacts/proposals/candidate.v1.json",
        comparison_report_file=comparison_path,
        review_scope_kind="global",
    )

    report = result.skeptical_eval_report
    assert report["review_outcome"] == "REJECT_FOR_NOW"
    assert any(item["reason_code"] == "POLICY_REGRESSION" for item in report["rejection_evidence"])


def test_train_api_builds_skeptical_eval_report(tmp_path: Path) -> None:
    comparison_path = _write_comparison_report(tmp_path / "comparison.json", sample_count=8)

    response = build_trinity_skeptical_eval(
        TrinitySkepticalEvalRequest(
            component_key="memory_retriever",
            artifact_family="retrieval_selection_policy",
            proposal_artifact_version="candidate.v1",
            proposal_ref="artifacts/proposals/candidate.v1.json",
            comparison_report_file=str(comparison_path),
            review_scope_kind="company",
            review_scope_value="company-1",
            overfitting_risks=("single customer slice",),
        )
    )

    assert response.component_key == "memory_retriever"
    assert response.skeptical_eval_report["confidence_summary"]["corpus_sufficiency"] in {
        "medium",
        "strong",
    }
    assert response.skeptical_eval_report["minority_report"]["overfitting_risks"] == [
        "single customer slice"
    ]


def test_train_cli_can_render_skeptical_eval_summary(tmp_path: Path, capsys) -> None:
    comparison_path = _write_comparison_report(tmp_path / "comparison.json", sample_count=4)

    exit_code = train_cli_main(
        [
            "build-skeptical-eval-report",
            "--component-key",
            "memory_retriever",
            "--artifact-family",
            "retrieval_selection_policy",
            "--proposal-artifact-version",
            "candidate.v1",
            "--proposal-ref",
            "artifacts/proposals/candidate.v1.json",
            "--comparison-report-file",
            str(comparison_path),
            "--review-scope-kind",
            "company",
            "--review-scope-value",
            "company-1",
            "--output-format",
            "summary",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "review_outcome:" in captured.out
    assert "INSUFFICIENT_CORPUS" in captured.out
