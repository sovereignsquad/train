from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from train_core.models import MetricDirection

COMPARISON_CONTRACT_VERSION = "train.comparison.v1alpha1"


class StandardComparisonRow(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    artifact_key: str = Field(min_length=1, max_length=120)
    version: str = Field(min_length=1, max_length=160)
    score: float | None = None
    status: str = Field(min_length=1, max_length=40)
    notes: str | None = None


class StandardComparisonDelta(BaseModel):
    from_label: str = Field(min_length=1, max_length=80)
    to_label: str = Field(min_length=1, max_length=80)
    score_delta: float | None = None
    improved: bool | None = None


class StandardComparisonReport(BaseModel):
    report_id: str = Field(min_length=1, max_length=160)
    generated_at: datetime
    contract_version: str = Field(min_length=1, max_length=120)
    evaluation_mode: str = Field(min_length=1, max_length=80)
    metric_name: str = Field(min_length=1, max_length=120)
    metric_direction: MetricDirection
    sample_count: int = Field(ge=1)
    corpus_fingerprint: str = Field(min_length=1, max_length=64)
    rows: tuple[StandardComparisonRow, ...] = Field(min_length=1)
    deltas: tuple[StandardComparisonDelta, ...] = ()
    table_markdown: str = Field(min_length=1)
    summary: str = Field(min_length=1)


def build_standard_comparison_report(
    *,
    report_id: str,
    generated_at: datetime,
    evaluation_mode: str,
    metric_name: str,
    metric_direction: MetricDirection,
    sample_count: int,
    corpus_fingerprint: str,
    rows: list[StandardComparisonRow],
    summary: str,
) -> StandardComparisonReport:
    deltas = _build_deltas(rows, metric_direction)
    return StandardComparisonReport(
        report_id=report_id,
        generated_at=generated_at,
        contract_version=COMPARISON_CONTRACT_VERSION,
        evaluation_mode=evaluation_mode,
        metric_name=metric_name,
        metric_direction=metric_direction,
        sample_count=sample_count,
        corpus_fingerprint=corpus_fingerprint,
        rows=tuple(rows),
        deltas=tuple(deltas),
        table_markdown=_build_table_markdown(rows, deltas),
        summary=summary,
    )


def _build_deltas(
    rows: list[StandardComparisonRow],
    metric_direction: MetricDirection,
) -> list[StandardComparisonDelta]:
    indexed = {row.label: row for row in rows}
    deltas: list[StandardComparisonDelta] = []
    for from_label, to_label in (("baseline", "candidate"), ("incumbent", "candidate")):
        from_row = indexed.get(from_label)
        to_row = indexed.get(to_label)
        if from_row is None or to_row is None:
            continue
        delta = None
        improved = None
        if from_row.score is not None and to_row.score is not None:
            delta = round(to_row.score - from_row.score, 6)
            improved = delta > 0 if metric_direction is MetricDirection.MAXIMIZE else delta < 0
        deltas.append(
            StandardComparisonDelta(
                from_label=from_label,
                to_label=to_label,
                score_delta=delta,
                improved=improved,
            )
        )
    return deltas


def _build_table_markdown(
    rows: list[StandardComparisonRow],
    deltas: list[StandardComparisonDelta],
) -> str:
    lines = [
        "| Label | Artifact | Version | Score | Status | Notes |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        score = "-" if row.score is None else f"{row.score:.6f}"
        notes = row.notes or ""
        lines.append(
            f"| {row.label} | {row.artifact_key} | {row.version} | {score} | {row.status} | {notes} |"
        )
    if deltas:
        lines.extend(["", "| Delta | Value |", "| --- | ---: |"])
        for delta in deltas:
            value = "-" if delta.score_delta is None else f"{delta.score_delta:.6f}"
            lines.append(f"| {delta.to_label} - {delta.from_label} | {value} |")
    return "\n".join(lines)
