from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from train_api.main import create_grader_suite_route, run_grader_suite_route
from train_core.cli import main as train_cli_main
from train_core.comparison import StandardComparisonRow, build_standard_comparison_report
from train_core.datasets import create_eval_dataset, delete_eval_dataset, get_eval_dataset
from train_core.db import SessionLocal, init_db
from train_core.grader_suites import create_grader_suite, get_grader_suite, run_grader_suite
from train_core.models import MetricDirection
from train_core.schemas import (
    EvalDatasetWrite,
    GraderSuiteRunRequest,
    GraderSuiteWrite,
)


def _write_comparison_report(path: Path) -> Path:
    report = build_standard_comparison_report(
        report_id="retrieval-suite.comparison",
        generated_at=datetime(2026, 5, 11, 10, 0, tzinfo=UTC),
        evaluation_mode="fixed_replay_corpus",
        metric_name="retrieval_selection_policy_fit",
        metric_direction=MetricDirection.MAXIMIZE,
        sample_count=8,
        corpus_fingerprint="grader123",
        rows=[
            StandardComparisonRow(
                label="baseline",
                artifact_key="retrieval_selection_policy",
                version="baseline.v1",
                score=0.78,
                status="evaluated",
                notes="fixture baseline",
            ),
            StandardComparisonRow(
                label="incumbent",
                artifact_key="retrieval_selection_policy",
                version="incumbent.v1",
                score=0.81,
                status="evaluated",
                notes="fixture incumbent",
            ),
            StandardComparisonRow(
                label="candidate",
                artifact_key="retrieval_selection_policy",
                version="candidate.v2",
                score=0.87,
                status="evaluated",
                notes="fixture candidate",
            ),
        ],
        summary="Fixture comparison for grader suite tests.",
    )
    path.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
    return path


def test_grader_suite_persists_and_runs(tmp_path: Path) -> None:
    init_db()
    dataset_key = "grader-suite-dataset"
    dataset_version = "2026-05-11.1"
    suite_key = "retrieval-core"
    suite_version = "2026-05-11.1"
    corpus_file = tmp_path / "corpus.json"
    corpus_file.write_text("{}", encoding="utf-8")
    comparison_path = _write_comparison_report(tmp_path / "comparison.json")
    output_path = tmp_path / "grader-run.json"

    with SessionLocal() as db:
        if get_eval_dataset(dataset_key, dataset_version, db) is not None:
            delete_eval_dataset(db, dataset_key, dataset_version)
        create_eval_dataset(
            db,
            EvalDatasetWrite(
                key=dataset_key,
                version=dataset_version,
                name="Grader Dataset",
                description="Dataset for persistent grader suites.",
                source_kind="trinity-retrieval",
                scope_kind="company",
                scope_value="company-1",
                items=(
                    {
                        "item_key": "corpus-1",
                        "path": str(corpus_file.resolve()),
                        "labels": {"slice": "core"},
                    },
                ),
                provenance={"purpose": "grader-suite"},
            ),
        )
        suite = create_grader_suite(
            db,
            dataset_key,
            dataset_version,
            GraderSuiteWrite(
                key=suite_key,
                version=suite_version,
                name="Retrieval Core Suite",
                description="Persistent retrieval grader suite.",
                proposal_family="retrieval_selection_policy",
                graders=(
                    {
                        "grader_key": "incumbent_delta",
                        "grader_kind": "code",
                        "entrypoint_ref": "builtin://candidate-vs-incumbent-delta",
                        "metric_name": "candidate_vs_incumbent_delta",
                        "pass_threshold": 0.03,
                    },
                    {
                        "grader_key": "retrieval_judge_ref",
                        "grader_kind": "model",
                        "entrypoint_ref": "model://gpt-5.5",
                        "metric_name": "retrieval_judge_reference",
                    },
                ),
                provenance={"owner": "tests"},
            ),
        )
        assert suite.ref == f"{dataset_key}@{dataset_version}:{suite_key}@{suite_version}"
        assert get_grader_suite(dataset_key, dataset_version, suite_key, suite_version, db) is not None

        result = run_grader_suite(
            dataset_key,
            dataset_version,
            suite_key,
            suite_version,
            GraderSuiteRunRequest(
                proposal_family="retrieval_selection_policy",
                proposal_artifact_version="candidate.v2",
                comparison_report_file=str(comparison_path.resolve()),
                output_path=str(output_path.resolve()),
            ),
            db,
        )
        assert result.output_path == str(output_path.resolve())
        assert result.suite_ref == f"{dataset_key}@{dataset_version}:{suite_key}@{suite_version}"
        assert any(item["grader_key"] == "incumbent_delta" and item["passed"] is True for item in result.grader_results)
        assert any(item["grader_key"] == "retrieval_judge_ref" and item["status"] == "reference_only" for item in result.grader_results)

        delete_eval_dataset(db, dataset_key, dataset_version)


def test_grader_suite_routes_and_cli(tmp_path: Path, capsys) -> None:
    init_db()
    dataset_key = "grader-route-dataset"
    dataset_version = "2026-05-11.1"
    suite_key = "route-suite"
    suite_version = "2026-05-11.1"
    corpus_file = tmp_path / "corpus.json"
    corpus_file.write_text("{}", encoding="utf-8")
    comparison_path = _write_comparison_report(tmp_path / "comparison.json")

    with SessionLocal() as db:
        if get_eval_dataset(dataset_key, dataset_version, db) is not None:
            delete_eval_dataset(db, dataset_key, dataset_version)
        create_eval_dataset(
            db,
            EvalDatasetWrite(
                key=dataset_key,
                version=dataset_version,
                name="Grader Route Dataset",
                description="Dataset for route and CLI tests.",
                source_kind="trinity-retrieval",
                scope_kind="company",
                scope_value="company-1",
                items=(
                    {
                        "item_key": "corpus-1",
                        "path": str(corpus_file.resolve()),
                        "labels": {"slice": "core"},
                    },
                ),
                provenance={"purpose": "route"},
            ),
        )
        suite = create_grader_suite_route(
            dataset_key,
            dataset_version,
            GraderSuiteWrite(
                key=suite_key,
                version=suite_version,
                name="Route Suite",
                description="Route-created suite.",
                proposal_family="retrieval_selection_policy",
                graders=(
                    {
                        "grader_key": "sample_count",
                        "grader_kind": "code",
                        "entrypoint_ref": "builtin://minimum-sample-count",
                        "metric_name": "sample_count",
                        "pass_threshold": 5,
                    },
                ),
                provenance={"kind": "route"},
            ),
            db=db,
        )
        assert suite.proposal_family == "retrieval_selection_policy"

        route_run = run_grader_suite_route(
            dataset_key,
            dataset_version,
            suite_key,
            suite_version,
            GraderSuiteRunRequest(
                proposal_family="retrieval_selection_policy",
                proposal_artifact_version="candidate.v2",
                comparison_report_file=str(comparison_path.resolve()),
            ),
            db=db,
        )
        assert route_run.grader_results[0]["passed"] is True

    exit_code = train_cli_main(
        [
            "run-grader-suite",
            "--dataset-key",
            dataset_key,
            "--dataset-version",
            dataset_version,
            "--suite-key",
            suite_key,
            "--suite-version",
            suite_version,
            "--proposal-family",
            "retrieval_selection_policy",
            "--proposal-artifact-version",
            "candidate.v2",
            "--comparison-report-file",
            str(comparison_path.resolve()),
            "--output-format",
            "summary",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Ran grader suite" in captured.out
    assert "sample_count" in captured.out

    with SessionLocal() as db:
        delete_eval_dataset(db, dataset_key, dataset_version)
