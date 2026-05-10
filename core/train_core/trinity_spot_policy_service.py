from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from train_core.schemas import (
    SpotReviewPolicyProposal,
    TrinitySpotPolicyProposalRead,
    TrinitySpotTrainingBundleRecord,
)
from train_core.trinity_trace_loader import load_trinity_spot_training_bundle


def propose_spot_review_policy_from_bundle_files(
    *,
    learner_kind: str,
    bundle_files: list[str | Path],
    proposal_output_path: str | Path | None = None,
    eval_output_path: str | Path | None = None,
    comparison_output_path: str | Path | None = None,
) -> TrinitySpotPolicyProposalRead:
    if learner_kind != "review-policy":
        raise ValueError("learner_kind is invalid")
    if not bundle_files:
        raise ValueError("At least one training bundle file is required.")

    bundles = [load_trinity_spot_training_bundle(path) for path in bundle_files]
    proposal = learn_spot_review_policy(bundles)
    eval_report = build_spot_review_policy_eval_report(bundles, proposal)
    comparison_report = build_spot_review_policy_comparison_report(eval_report, proposal)

    proposal_path = _write_json_file(proposal_output_path, proposal.model_dump(mode="json"))
    eval_path = _write_json_file(eval_output_path, eval_report)
    comparison_path = _write_json_file(comparison_output_path, comparison_report)
    return TrinitySpotPolicyProposalRead(
        learner_kind=learner_kind,
        bundle_count=len(bundles),
        proposal=proposal,
        eval_report=eval_report,
        comparison_report=comparison_report,
        proposal_path=str(proposal_path) if proposal_path is not None else None,
        eval_output_path=str(eval_path) if eval_path is not None else None,
        comparison_output_path=str(comparison_path) if comparison_path is not None else None,
    )


def learn_spot_review_policy(
    bundles: list[TrinitySpotTrainingBundleRecord],
    *,
    created_at: datetime | None = None,
) -> SpotReviewPolicyProposal:
    if not bundles:
        raise ValueError("At least one Spot training bundle is required.")
    ordered = sorted(bundles, key=lambda bundle: (bundle.exported_at, bundle.bundle_id))
    scope_kind, scope_value = _infer_spot_policy_scope(ordered)
    negatives = [
        bundle.spot_reasoning_result.confidence_bundle.combined_confidence
        for bundle in ordered
        if bundle.spot_review_outcome.final_label == "Not Antisemitic"
        and bundle.spot_review_outcome.disposition == "CONFIRMED_NEGATIVE"
    ]
    # This first bounded learner only derives the negative auto-approve threshold.
    # Positive and fallback behavior remain explicit fixed policy flags.
    threshold = round(sum(negatives) / len(negatives), 4) if negatives else 0.72
    created = created_at or max(bundle.exported_at for bundle in ordered)
    return SpotReviewPolicyProposal(
        artifact_key="spot_review_policy",
        version=f"spot_review_policy.review.{created.strftime('%Y%m%d%H%M%S')}",
        scope_kind=scope_kind,
        scope_value=scope_value,
        created_at=created,
        source_project="train",
        auto_approve_negative_threshold=threshold,
        positive_review_required=True,
        default_review_required=True,
        notes=(
            f"Learned from {len(ordered)} Spot review-policy bundle(s); "
            f"negative auto-approve threshold derived from confirmed negative rows."
        ),
        contract_version="trinity.spot.v1alpha1",
    )


def build_spot_review_policy_eval_report(
    bundles: list[TrinitySpotTrainingBundleRecord],
    proposal: SpotReviewPolicyProposal,
) -> dict[str, object]:
    negative_count = 0
    positive_count = 0
    corrected_count = 0
    auto_approve_eligible_negative_count = 0
    review_required_positive_count = 0
    for bundle in bundles:
        outcome = bundle.spot_review_outcome
        result = bundle.spot_reasoning_result
        if outcome.disposition == "CONFIRMED_NEGATIVE":
            negative_count += 1
            if result.confidence_bundle.combined_confidence >= proposal.auto_approve_negative_threshold:
                auto_approve_eligible_negative_count += 1
        elif outcome.disposition == "CONFIRMED_POSITIVE":
            positive_count += 1
            if result.review_required:
                review_required_positive_count += 1
        elif outcome.disposition == "CORRECTED":
            corrected_count += 1

    return {
        "report_id": f"{proposal.version}.eval",
        "generated_at": max(bundle.exported_at for bundle in bundles).isoformat(),
        "learner_kind": "review-policy",
        "bundle_count": len(bundles),
        "candidate_artifact_key": proposal.artifact_key,
        "candidate_version": proposal.version,
        "scope_kind": proposal.scope_kind,
        "scope_value": proposal.scope_value,
        "auto_approve_negative_threshold": proposal.auto_approve_negative_threshold,
        "negative_count": negative_count,
        "positive_count": positive_count,
        "corrected_count": corrected_count,
        "auto_approve_eligible_negative_count": auto_approve_eligible_negative_count,
        "review_required_positive_count": review_required_positive_count,
        "summary": (
            f"Spot review policy proposal {proposal.version} evaluated on {len(bundles)} "
            "bundle(s)."
        ),
    }


def build_spot_review_policy_comparison_report(
    eval_report: dict[str, object],
    proposal: SpotReviewPolicyProposal,
) -> dict[str, object]:
    score = 1.0 if eval_report.get("review_required_positive_count", 0) == eval_report.get("positive_count", 0) else 0.5
    return {
        "report_id": f"{proposal.version}.comparison",
        "evaluation_mode": "fixed_replay_corpus",
        "metric_name": "spot_review_policy_fit",
        "rows": [
            {
                "label": "candidate",
                "artifact_key": proposal.artifact_key,
                "version": proposal.version,
                "scope_kind": proposal.scope_kind,
                "scope_value": proposal.scope_value,
                "score": score,
                "status": "evaluated",
                "notes": "Scored on fixed Spot review-policy bundle corpus.",
            }
        ],
        "summary": str(eval_report["summary"]),
    }


def _write_json_file(path: str | Path | None, payload: dict[str, object]) -> Path | None:
    if path is None:
        return None
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return output_path


def _infer_spot_policy_scope(
    bundles: list[TrinitySpotTrainingBundleRecord],
) -> tuple[str, str | None]:
    # Keep the first Spot scope contract intentionally narrow: one-company corpora
    # produce a company-scoped artifact, and mixed corpora fall back to global.
    company_ids = {
        str(bundle.spot_reasoning_request.company_id).strip().lower() for bundle in bundles
    }
    if len(company_ids) == 1:
        return "company", next(iter(company_ids))
    return "global", None
