from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from train_core.comparison import StandardComparisonReport
from train_core.datasets import EvalDatasetError, get_eval_dataset
from train_core.db import SessionLocal
from train_core.models import GraderSuiteRecord
from train_core.schemas import (
    GraderDefinition,
    GraderSuiteRead,
    GraderSuiteRunRead,
    GraderSuiteRunRequest,
    GraderSuiteWrite,
)


class GraderSuiteError(ValueError):
    """Raised when a grader suite operation is invalid."""


@dataclass(frozen=True)
class GraderSuiteDefinition:
    dataset_key: str
    dataset_version: str
    dataset_ref: str
    key: str
    version: str
    ref: str
    name: str
    description: str
    proposal_family: str
    graders: tuple[GraderDefinition, ...]
    provenance: dict[str, object]


def list_grader_suites(
    dataset_key: str,
    dataset_version: str,
    db: Session | None = None,
) -> list[GraderSuiteDefinition]:
    if db is None:
        with SessionLocal() as owned_session:
            return _list_grader_suites(owned_session, dataset_key, dataset_version)
    return _list_grader_suites(db, dataset_key, dataset_version)


def get_grader_suite(
    dataset_key: str,
    dataset_version: str,
    key: str,
    version: str,
    db: Session | None = None,
) -> GraderSuiteDefinition | None:
    if db is None:
        with SessionLocal() as owned_session:
            return _get_grader_suite(owned_session, dataset_key, dataset_version, key, version)
    return _get_grader_suite(db, dataset_key, dataset_version, key, version)


def create_grader_suite(
    db: Session,
    dataset_key: str,
    dataset_version: str,
    payload: GraderSuiteWrite,
) -> GraderSuiteDefinition:
    _require_grader_suite_tables(db)
    if get_eval_dataset(dataset_key, dataset_version, db) is None:
        raise EvalDatasetError(
            f"Eval dataset '{dataset_key}' version '{dataset_version}' was not found."
        )
    if _get_grader_suite(db, dataset_key, dataset_version, payload.key, payload.version) is not None:
        raise GraderSuiteError(
            f"Grader suite '{payload.key}' version '{payload.version}' already exists."
        )
    row = GraderSuiteRecord(
        dataset_key=dataset_key,
        dataset_version=dataset_version,
        key=payload.key,
        version=payload.version,
        name=payload.name,
        description=payload.description,
        proposal_family=payload.proposal_family,
        graders_json=json.dumps([grader.model_dump(mode="json") for grader in payload.graders], sort_keys=True),
        provenance_json=json.dumps(payload.provenance, sort_keys=True),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _row_to_definition(row)


def delete_grader_suite(
    db: Session,
    dataset_key: str,
    dataset_version: str,
    key: str,
    version: str,
) -> None:
    _require_grader_suite_tables(db)
    row = (
        db.query(GraderSuiteRecord)
        .filter(
            GraderSuiteRecord.dataset_key == dataset_key,
            GraderSuiteRecord.dataset_version == dataset_version,
            GraderSuiteRecord.key == key,
            GraderSuiteRecord.version == version,
        )
        .one_or_none()
    )
    if row is None:
        raise GraderSuiteError(
            f"Grader suite '{key}' version '{version}' was not found for dataset "
            f"'{dataset_key}' version '{dataset_version}'."
        )
    db.delete(row)
    db.commit()


def run_grader_suite(
    dataset_key: str,
    dataset_version: str,
    key: str,
    version: str,
    payload: GraderSuiteRunRequest,
    db: Session | None = None,
) -> GraderSuiteRunRead:
    if db is None:
        with SessionLocal() as owned_session:
            return _run_grader_suite(owned_session, dataset_key, dataset_version, key, version, payload)
    return _run_grader_suite(db, dataset_key, dataset_version, key, version, payload)


def serialize_grader_suite(definition: GraderSuiteDefinition) -> GraderSuiteRead:
    return GraderSuiteRead(**definition.__dict__)


def _list_grader_suites(
    db: Session,
    dataset_key: str,
    dataset_version: str,
) -> list[GraderSuiteDefinition]:
    if not _grader_suite_tables_exist(db):
        return []
    rows = (
        db.query(GraderSuiteRecord)
        .filter(
            GraderSuiteRecord.dataset_key == dataset_key,
            GraderSuiteRecord.dataset_version == dataset_version,
        )
        .order_by(GraderSuiteRecord.key.asc(), GraderSuiteRecord.version.asc())
        .all()
    )
    return [_row_to_definition(row) for row in rows]


def _get_grader_suite(
    db: Session,
    dataset_key: str,
    dataset_version: str,
    key: str,
    version: str,
) -> GraderSuiteDefinition | None:
    if not _grader_suite_tables_exist(db):
        return None
    row = (
        db.query(GraderSuiteRecord)
        .filter(
            GraderSuiteRecord.dataset_key == dataset_key,
            GraderSuiteRecord.dataset_version == dataset_version,
            GraderSuiteRecord.key == key,
            GraderSuiteRecord.version == version,
        )
        .one_or_none()
    )
    return None if row is None else _row_to_definition(row)


def _run_grader_suite(
    db: Session,
    dataset_key: str,
    dataset_version: str,
    key: str,
    version: str,
    payload: GraderSuiteRunRequest,
) -> GraderSuiteRunRead:
    suite = _get_grader_suite(db, dataset_key, dataset_version, key, version)
    if suite is None:
        raise GraderSuiteError(
            f"Grader suite '{key}' version '{version}' was not found for dataset "
            f"'{dataset_key}' version '{dataset_version}'."
        )
    if suite.proposal_family != payload.proposal_family:
        raise GraderSuiteError("proposal_family does not match the persistent grader suite")

    comparison_path = Path(payload.comparison_report_file)
    comparison = StandardComparisonReport.model_validate(
        json.loads(comparison_path.read_text(encoding="utf-8"))
    )
    artifact_inputs = {
        str(item["grader_key"]): str(item["path"])
        for item in payload.evaluator_artifact_files
    }
    results = tuple(_run_one_grader(grader, comparison, artifact_inputs) for grader in suite.graders)
    disagreements = tuple(_build_disagreements(results))
    summary = (
        f"Ran grader suite {suite.ref} against proposal {payload.proposal_artifact_version} "
        f"using comparison report {comparison.report_id}."
    )
    report = {
        "suite_ref": suite.ref,
        "dataset_ref": suite.dataset_ref,
        "proposal_family": suite.proposal_family,
        "proposal_artifact_version": payload.proposal_artifact_version,
        "comparison_ref": str(comparison_path),
        "generated_at": datetime.now(UTC).isoformat(),
        "grader_results": results,
        "disagreements": disagreements,
        "summary": summary,
    }
    output_path = _write_json_file(payload.output_path, report)
    return GraderSuiteRunRead(
        **report,
        output_path=str(output_path) if output_path is not None else None,
    )


def _run_one_grader(
    grader: GraderDefinition,
    comparison: StandardComparisonReport,
    artifact_inputs: dict[str, str],
) -> dict[str, object]:
    if grader.grader_kind == "model":
        return _import_external_evaluator_result(
            grader,
            artifact_inputs,
            expected_kind="model",
        )
    if grader.grader_kind == "human":
        return _import_external_evaluator_result(
            grader,
            artifact_inputs,
            expected_kind="human",
        )
    if grader.entrypoint_ref == "builtin://candidate-vs-incumbent-delta":
        delta = _candidate_delta(comparison, "incumbent")
        return _graded_result(grader, delta, "candidate-incumbent delta")
    if grader.entrypoint_ref == "builtin://candidate-vs-baseline-delta":
        delta = _candidate_delta(comparison, "baseline")
        return _graded_result(grader, delta, "candidate-baseline delta")
    if grader.entrypoint_ref == "builtin://minimum-sample-count":
        score = float(comparison.sample_count)
        return _graded_result(grader, score, "comparison sample count")
    return {
        "grader_key": grader.grader_key,
        "grader_kind": grader.grader_kind,
        "entrypoint_ref": grader.entrypoint_ref,
        "metric_name": grader.metric_name,
        "status": "unknown_grader",
        "score": None,
        "passed": None,
        "notes": "Unknown grader entrypoint_ref.",
    }


def _import_external_evaluator_result(
    grader: GraderDefinition,
    artifact_inputs: dict[str, str],
    *,
    expected_kind: str,
) -> dict[str, object]:
    artifact_path = artifact_inputs.get(grader.grader_key)
    if artifact_path is None:
        return {
            "grader_key": grader.grader_key,
            "grader_kind": grader.grader_kind,
            "entrypoint_ref": grader.entrypoint_ref,
            "metric_name": grader.metric_name,
            "status": "missing_artifact",
            "score": None,
            "passed": None,
            "notes": f"No imported {expected_kind} evaluator artifact was provided for this grader.",
        }
    payload = json.loads(Path(artifact_path).read_text(encoding="utf-8"))
    artifact_kind = str(payload.get("grader_kind") or payload.get("evaluator_kind") or "").strip()
    if artifact_kind and artifact_kind != expected_kind:
        raise GraderSuiteError(
            f"Imported evaluator artifact for '{grader.grader_key}' has kind '{artifact_kind}', "
            f"expected '{expected_kind}'."
        )
    return {
        "grader_key": grader.grader_key,
        "grader_kind": grader.grader_kind,
        "entrypoint_ref": grader.entrypoint_ref,
        "metric_name": grader.metric_name,
        "status": "imported",
        "score": payload.get("score"),
        "pass_threshold": grader.pass_threshold,
        "passed": payload.get("passed"),
        "artifact_ref": artifact_path,
        "notes": str(payload.get("notes") or f"Imported {expected_kind} evaluator artifact."),
        "provenance": payload.get("provenance") or {},
    }


def _graded_result(
    grader: GraderDefinition,
    score: float | None,
    note_prefix: str,
) -> dict[str, object]:
    passed = None
    if score is not None and grader.pass_threshold is not None:
        passed = score >= grader.pass_threshold
    return {
        "grader_key": grader.grader_key,
        "grader_kind": grader.grader_kind,
        "entrypoint_ref": grader.entrypoint_ref,
        "metric_name": grader.metric_name,
        "status": "evaluated" if score is not None else "missing_signal",
        "score": score,
        "pass_threshold": grader.pass_threshold,
        "passed": passed,
        "notes": f"{note_prefix} evaluated from comparison artifact.",
    }


def _candidate_delta(comparison: StandardComparisonReport, from_label: str) -> float | None:
    for delta in comparison.deltas:
        if delta.from_label == from_label and delta.to_label == "candidate":
            return delta.score_delta
    return None


def _build_disagreements(results: tuple[dict[str, object], ...]) -> list[dict[str, object]]:
    graded = [item for item in results if item.get("passed") is not None]
    disagreements: list[dict[str, object]] = []
    for index, left in enumerate(graded):
        for right in graded[index + 1 :]:
            if left.get("passed") == right.get("passed"):
                continue
            disagreements.append(
                {
                    "left_grader_key": left.get("grader_key"),
                    "left_grader_kind": left.get("grader_kind"),
                    "left_passed": left.get("passed"),
                    "right_grader_key": right.get("grader_key"),
                    "right_grader_kind": right.get("grader_kind"),
                    "right_passed": right.get("passed"),
                    "summary": (
                        f"{left.get('grader_key')} ({left.get('grader_kind')}) disagrees with "
                        f"{right.get('grader_key')} ({right.get('grader_kind')})."
                    ),
                }
            )
    return disagreements


def _row_to_definition(row: GraderSuiteRecord) -> GraderSuiteDefinition:
    graders = tuple(GraderDefinition.model_validate(item) for item in json.loads(row.graders_json))
    provenance = dict(json.loads(row.provenance_json))
    dataset_ref = f"{row.dataset_key}@{row.dataset_version}"
    return GraderSuiteDefinition(
        dataset_key=row.dataset_key,
        dataset_version=row.dataset_version,
        dataset_ref=dataset_ref,
        key=row.key,
        version=row.version,
        ref=f"{dataset_ref}:{row.key}@{row.version}",
        name=row.name,
        description=row.description,
        proposal_family=row.proposal_family,
        graders=graders,
        provenance=provenance,
    )


def _grader_suite_tables_exist(db: Session) -> bool:
    inspector = inspect(db.bind)
    return "grader_suites" in set(inspector.get_table_names())


def _require_grader_suite_tables(db: Session) -> None:
    if not _grader_suite_tables_exist(db):
        raise GraderSuiteError(
            "Persistent grader suite registry is unavailable until database migrations have been applied."
        )


def _write_json_file(path: str | None, payload: dict[str, Any]) -> Path | None:
    if path is None:
        return None
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return output_path
