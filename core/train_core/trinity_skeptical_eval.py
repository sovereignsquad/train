from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from train_core.comparison import StandardComparisonReport, StandardComparisonRow
from train_core.schemas import (
    SkepticalEvalDisproofTestInput,
    SkepticalEvalRejectionEvidenceInput,
    TrinitySkepticalEvalRead,
)

SKEPTICAL_EVAL_CONTRACT_VERSION = "train.skeptical_eval.v1alpha1"


class SkepticalEvalRejectionEvidence(BaseModel):
    reason_code: str = Field(min_length=1, max_length=80)
    severity: str = Field(min_length=1, max_length=20)
    evidence_summary: str = Field(min_length=1)
    supporting_signal: str = Field(min_length=1)
    blocking: bool


class SkepticalEvalMinorityReport(BaseModel):
    skeptical_summary: str = Field(min_length=1)
    hidden_confounds: tuple[str, ...] = ()
    overfitting_risks: tuple[str, ...] = ()
    weak_assumptions: tuple[str, ...] = ()
    disconfirming_signals: tuple[str, ...] = ()


class SkepticalEvalConfidenceSummary(BaseModel):
    corpus_sufficiency: str = Field(min_length=1, max_length=20)
    reproducibility: str = Field(min_length=1, max_length=20)
    signal_clarity: str = Field(min_length=1, max_length=20)


class SkepticalEvalDisproofTest(BaseModel):
    test_name: str = Field(min_length=1, max_length=160)
    purpose: str = Field(min_length=1)
    expected_failure_signal: str = Field(min_length=1)


class SkepticalEvalReport(BaseModel):
    contract_version: str = Field(min_length=1, max_length=120)
    report_type: str = Field(min_length=1, max_length=80)
    component_key: str = Field(min_length=1, max_length=120)
    artifact_family: str = Field(min_length=1, max_length=120)
    proposal_artifact_version: str = Field(min_length=1, max_length=160)
    proposal_ref: str = Field(min_length=1)
    comparison_ref: str = Field(min_length=1)
    review_scope_kind: str = Field(min_length=1, max_length=40)
    review_scope_value: str | None = None
    generated_at: str = Field(min_length=1, max_length=80)
    review_outcome: str = Field(min_length=1, max_length=40)
    promotion_readiness: str = Field(min_length=1, max_length=40)
    primary_decision_summary: str = Field(min_length=1)
    rejection_evidence: tuple[SkepticalEvalRejectionEvidence, ...]
    minority_report: SkepticalEvalMinorityReport
    confidence_summary: SkepticalEvalConfidenceSummary
    next_disproof_tests: tuple[SkepticalEvalDisproofTest, ...]


def build_skeptical_eval_report(
    *,
    component_key: str,
    artifact_family: str,
    proposal_artifact_version: str,
    proposal_ref: str,
    comparison_report_file: str | Path,
    review_scope_kind: str,
    review_scope_value: str | None = None,
    minimum_sample_count: int = 5,
    minimum_improvement_delta: float = 0.02,
    hidden_confounds: tuple[str, ...] = (),
    overfitting_risks: tuple[str, ...] = (),
    weak_assumptions: tuple[str, ...] = (),
    disconfirming_signals: tuple[str, ...] = (),
    additional_rejection_evidence: tuple[SkepticalEvalRejectionEvidenceInput, ...] = (),
    additional_disproof_tests: tuple[SkepticalEvalDisproofTestInput, ...] = (),
    skeptical_eval_output_path: str | Path | None = None,
) -> TrinitySkepticalEvalRead:
    comparison_path = Path(comparison_report_file)
    comparison = _load_standard_comparison_report(comparison_path)
    indexed_rows = {row.label: row for row in comparison.rows}
    candidate_row = indexed_rows.get("candidate")
    if candidate_row is None:
        raise ValueError("Comparison report must contain a candidate row")

    incumbent_row = indexed_rows.get("incumbent")
    baseline_row = indexed_rows.get("baseline")
    evidence = _build_rejection_evidence(
        comparison=comparison,
        candidate_row=candidate_row,
        incumbent_row=incumbent_row,
        baseline_row=baseline_row,
        minimum_sample_count=minimum_sample_count,
        minimum_improvement_delta=minimum_improvement_delta,
        additional_rejection_evidence=additional_rejection_evidence,
    )
    confidence_summary = _build_confidence_summary(
        comparison=comparison,
        candidate_row=candidate_row,
        incumbent_row=incumbent_row,
        baseline_row=baseline_row,
        evidence=evidence,
        minimum_sample_count=minimum_sample_count,
        minimum_improvement_delta=minimum_improvement_delta,
    )
    promotion_readiness = "NOT_PROMOTION_READY" if any(item.blocking for item in evidence) else "PROMOTION_READY"
    review_outcome = _determine_review_outcome(
        comparison=comparison,
        evidence=evidence,
        minimum_improvement_delta=minimum_improvement_delta,
    )
    minority_report = _build_minority_report(
        evidence=evidence,
        hidden_confounds=hidden_confounds,
        overfitting_risks=overfitting_risks,
        weak_assumptions=weak_assumptions,
        disconfirming_signals=disconfirming_signals,
    )
    next_disproof_tests = _build_disproof_tests(
        evidence=evidence,
        additional_disproof_tests=additional_disproof_tests,
    )
    report = SkepticalEvalReport(
        contract_version=SKEPTICAL_EVAL_CONTRACT_VERSION,
        report_type="skeptical-eval-report",
        component_key=component_key,
        artifact_family=artifact_family,
        proposal_artifact_version=proposal_artifact_version,
        proposal_ref=proposal_ref,
        comparison_ref=str(comparison_path),
        review_scope_kind=review_scope_kind,
        review_scope_value=review_scope_value,
        generated_at=comparison.generated_at.isoformat(),
        review_outcome=review_outcome,
        promotion_readiness=promotion_readiness,
        primary_decision_summary=_build_primary_decision_summary(
            comparison=comparison,
            evidence=evidence,
            review_outcome=review_outcome,
            promotion_readiness=promotion_readiness,
        ),
        rejection_evidence=tuple(evidence),
        minority_report=minority_report,
        confidence_summary=confidence_summary,
        next_disproof_tests=tuple(next_disproof_tests),
    )
    output_path = _write_json_file(skeptical_eval_output_path, report.model_dump(mode="json"))
    return TrinitySkepticalEvalRead(
        component_key=component_key,
        artifact_family=artifact_family,
        proposal_artifact_version=proposal_artifact_version,
        skeptical_eval_report=report.model_dump(mode="json"),
        skeptical_eval_output_path=str(output_path) if output_path is not None else None,
    )


def _load_standard_comparison_report(path: Path) -> StandardComparisonReport:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return StandardComparisonReport.model_validate(payload)


def _build_rejection_evidence(
    *,
    comparison: StandardComparisonReport,
    candidate_row: StandardComparisonRow,
    incumbent_row: StandardComparisonRow | None,
    baseline_row: StandardComparisonRow | None,
    minimum_sample_count: int,
    minimum_improvement_delta: float,
    additional_rejection_evidence: tuple[SkepticalEvalRejectionEvidenceInput, ...],
) -> list[SkepticalEvalRejectionEvidence]:
    evidence: list[SkepticalEvalRejectionEvidence] = []
    if comparison.sample_count < minimum_sample_count:
        evidence.append(
            SkepticalEvalRejectionEvidence(
                reason_code="INSUFFICIENT_CORPUS",
                severity="HIGH",
                evidence_summary=(
                    f"Comparison corpus has {comparison.sample_count} sample(s), below the "
                    f"minimum skeptical threshold of {minimum_sample_count}."
                ),
                supporting_signal=f"sample_count={comparison.sample_count}",
                blocking=True,
            )
        )
    if candidate_row.status != "evaluated" or candidate_row.score is None:
        evidence.append(
            SkepticalEvalRejectionEvidence(
                reason_code="UNSCORABLE_CANDIDATE",
                severity="HIGH",
                evidence_summary="Candidate row is not fully scored, so the proposal cannot be trusted for promotion review.",
                supporting_signal=f"candidate_status={candidate_row.status}",
                blocking=True,
            )
        )
    evidence.extend(
        _comparison_gap_evidence(
            baseline_row=baseline_row,
            incumbent_row=incumbent_row,
            candidate_row=candidate_row,
            metric_name=comparison.metric_name,
            minimum_improvement_delta=minimum_improvement_delta,
        )
    )
    evidence.extend(
        SkepticalEvalRejectionEvidence.model_validate(item.model_dump(mode="json"))
        for item in additional_rejection_evidence
    )
    return evidence


def _comparison_gap_evidence(
    *,
    baseline_row: StandardComparisonRow | None,
    incumbent_row: StandardComparisonRow | None,
    candidate_row: StandardComparisonRow,
    metric_name: str,
    minimum_improvement_delta: float,
) -> list[SkepticalEvalRejectionEvidence]:
    evidence: list[SkepticalEvalRejectionEvidence] = []
    if incumbent_row is None or incumbent_row.score is None:
        evidence.append(
            SkepticalEvalRejectionEvidence(
                reason_code="INCOMPLETE_INCUMBENT_EVIDENCE",
                severity="HIGH",
                evidence_summary="Incumbent artifact was not replay-scored, so risky proposal review lacks a direct incumbent comparison.",
                supporting_signal="incumbent score unavailable",
                blocking=True,
            )
        )
    else:
        delta = (candidate_row.score or 0.0) - incumbent_row.score
        if delta <= 0.0:
            evidence.append(
                SkepticalEvalRejectionEvidence(
                    reason_code="POLICY_REGRESSION",
                    severity="HIGH",
                    evidence_summary="Candidate does not outperform the incumbent on the fixed replay corpus.",
                    supporting_signal=f"{metric_name} delta vs incumbent={delta:.6f}",
                    blocking=True,
                )
            )
        elif delta < minimum_improvement_delta:
            evidence.append(
                SkepticalEvalRejectionEvidence(
                    reason_code="UNCLEAR_CAUSALITY",
                    severity="MEDIUM",
                    evidence_summary="Candidate gain over incumbent is too small to trust without stronger disproof coverage.",
                    supporting_signal=f"{metric_name} delta vs incumbent={delta:.6f}",
                    blocking=True,
                )
            )
    if baseline_row is not None and baseline_row.score is not None and candidate_row.score is not None:
        baseline_delta = candidate_row.score - baseline_row.score
        if baseline_delta <= 0.0:
            evidence.append(
                SkepticalEvalRejectionEvidence(
                    reason_code="WEAK_GENERALIZATION",
                    severity="MEDIUM",
                    evidence_summary="Candidate does not exceed the provided baseline on the same replay corpus.",
                    supporting_signal=f"{metric_name} delta vs baseline={baseline_delta:.6f}",
                    blocking=False,
                )
            )
    return evidence


def _build_confidence_summary(
    *,
    comparison: StandardComparisonReport,
    candidate_row: StandardComparisonRow,
    incumbent_row: StandardComparisonRow | None,
    baseline_row: StandardComparisonRow | None,
    evidence: list[SkepticalEvalRejectionEvidence],
    minimum_sample_count: int,
    minimum_improvement_delta: float,
) -> SkepticalEvalConfidenceSummary:
    corpus_sufficiency = "weak"
    if comparison.sample_count >= minimum_sample_count * 2:
        corpus_sufficiency = "strong"
    elif comparison.sample_count >= minimum_sample_count:
        corpus_sufficiency = "medium"

    reproducibility = "weak"
    if incumbent_row is not None and incumbent_row.score is not None:
        reproducibility = "medium"
        if baseline_row is not None and baseline_row.score is not None:
            reproducibility = "strong"

    signal_clarity = "weak"
    if candidate_row.score is not None and incumbent_row is not None and incumbent_row.score is not None:
        delta = candidate_row.score - incumbent_row.score
        if delta >= minimum_improvement_delta and not any(item.blocking for item in evidence):
            signal_clarity = "strong"
        elif delta > 0.0:
            signal_clarity = "medium"

    return SkepticalEvalConfidenceSummary(
        corpus_sufficiency=corpus_sufficiency,
        reproducibility=reproducibility,
        signal_clarity=signal_clarity,
    )


def _determine_review_outcome(
    *,
    comparison: StandardComparisonReport,
    evidence: list[SkepticalEvalRejectionEvidence],
    minimum_improvement_delta: float,
) -> str:
    incumbent_delta = _candidate_delta(comparison, "incumbent")
    if incumbent_delta is not None and incumbent_delta <= 0.0:
        return "REJECT_FOR_NOW"
    if any(item.blocking for item in evidence):
        return "HOLD_FOR_MORE_EVIDENCE"
    if incumbent_delta is not None and incumbent_delta < minimum_improvement_delta:
        return "HOLD_FOR_MORE_EVIDENCE"
    return "ADVANCE_WITH_CAUTION"


def _build_primary_decision_summary(
    *,
    comparison: StandardComparisonReport,
    evidence: list[SkepticalEvalRejectionEvidence],
    review_outcome: str,
    promotion_readiness: str,
) -> str:
    blocking_codes = [item.reason_code for item in evidence if item.blocking]
    if review_outcome == "REJECT_FOR_NOW":
        return (
            f"Candidate is not promotion-ready because the fixed replay comparison shows no honest "
            f"improvement over the incumbent. Blocking evidence: {', '.join(blocking_codes) or 'none'}."
        )
    if promotion_readiness == "NOT_PROMOTION_READY":
        return (
            f"Candidate remains not promotion-ready because skeptical review found unresolved blocking "
            f"evidence on top of comparison report {comparison.report_id}."
        )
    return (
        f"Candidate may advance for human review, but only with explicit skepticism preserved from "
        f"comparison report {comparison.report_id}."
    )


def _build_minority_report(
    *,
    evidence: list[SkepticalEvalRejectionEvidence],
    hidden_confounds: tuple[str, ...],
    overfitting_risks: tuple[str, ...],
    weak_assumptions: tuple[str, ...],
    disconfirming_signals: tuple[str, ...],
) -> SkepticalEvalMinorityReport:
    blocking_summaries = [item.evidence_summary for item in evidence if item.blocking]
    skeptical_summary = (
        blocking_summaries[0]
        if blocking_summaries
        else "The apparent gain is promising, but the proposal should still be treated as vulnerable to over-read."
    )
    return SkepticalEvalMinorityReport(
        skeptical_summary=skeptical_summary,
        hidden_confounds=hidden_confounds,
        overfitting_risks=overfitting_risks,
        weak_assumptions=weak_assumptions,
        disconfirming_signals=disconfirming_signals,
    )


def _build_disproof_tests(
    *,
    evidence: list[SkepticalEvalRejectionEvidence],
    additional_disproof_tests: tuple[SkepticalEvalDisproofTestInput, ...],
) -> list[SkepticalEvalDisproofTest]:
    tests: list[SkepticalEvalDisproofTest] = []
    seen_reason_codes = {item.reason_code for item in evidence}
    if "INSUFFICIENT_CORPUS" in seen_reason_codes:
        tests.append(
            SkepticalEvalDisproofTest(
                test_name="larger holdout replay",
                purpose="check whether the proposal survives a broader replay slice",
                expected_failure_signal="candidate advantage disappears when the corpus expands",
            )
        )
    if "INCOMPLETE_INCUMBENT_EVIDENCE" in seen_reason_codes:
        tests.append(
            SkepticalEvalDisproofTest(
                test_name="incumbent artifact replay",
                purpose="score the real incumbent artifact on the same corpus",
                expected_failure_signal="candidate advantage cannot be confirmed against the actual incumbent",
            )
        )
    if "POLICY_REGRESSION" in seen_reason_codes or "UNCLEAR_CAUSALITY" in seen_reason_codes:
        tests.append(
            SkepticalEvalDisproofTest(
                test_name="slice regression triage",
                purpose="find the replay slices where the candidate loses or only barely wins",
                expected_failure_signal="candidate improvement is isolated to one narrow slice",
            )
        )
    tests.extend(
        SkepticalEvalDisproofTest.model_validate(item.model_dump(mode="json"))
        for item in additional_disproof_tests
    )
    if not tests:
        tests.append(
            SkepticalEvalDisproofTest(
                test_name="cross-slice holdout replay",
                purpose="check whether the observed gain survives outside the initial replay slice",
                expected_failure_signal="candidate score advantage fails to reproduce on a nearby holdout corpus",
            )
        )
    return tests


def _candidate_delta(comparison: StandardComparisonReport, from_label: str) -> float | None:
    for delta in comparison.deltas:
        if delta.from_label == from_label and delta.to_label == "candidate":
            return delta.score_delta
    return None


def _write_json_file(path: str | Path | None, payload: dict[str, Any]) -> Path | None:
    if path is None:
        return None
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return output_path
