from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from train_core.trinity_trace_loader import load_trinity_spot_training_bundle


def _bundle_payload() -> dict[str, object]:
    return {
        "bundle_id": "bundle-spot-1",
        "bundle_type": "spot-review-policy-learning",
        "exported_at": datetime(2026, 5, 9, 12, 0, tzinfo=UTC).isoformat(),
        "spot_reasoning_request": {
            "company_id": "company-1",
            "run_id": "run-1",
            "row_ref": "sheet1:42",
            "language": "de",
            "message_text": "We should boycott the zionists everywhere.",
            "occurred_at": datetime(2026, 5, 9, 12, 0, tzinfo=UTC).isoformat(),
            "metadata": {},
            "contract_version": "trinity.spot.v1alpha1",
        },
        "spot_reasoning_result": {
            "company_id": "company-1",
            "run_id": "run-1",
            "row_ref": "sheet1:42",
            "generated_at": datetime(2026, 5, 9, 12, 0, tzinfo=UTC).isoformat(),
            "candidates": (
                {
                    "candidate_key": "review",
                    "interpretation": "Needs review.",
                    "rationale": "Ambiguous message.",
                    "threat_label_hint": "Structural Antisemitism",
                    "review_recommended": True,
                },
            ),
            "selected_candidate_key": "review",
            "confidence_bundle": {
                "generator_confidence": 0.61,
                "refiner_confidence": 0.65,
                "evaluator_confidence": 0.59,
                "frontier_confidence": 0.61,
                "combined_confidence": 0.61,
                "disagreement_severity": 0.32,
            },
            "review_required": True,
            "review_reason": "Positive threat classification stays review-required.",
            "policy_sensitive": True,
            "automatic_disposition": "review_required",
            "human_override_allowed": True,
            "deeper_analysis_available": True,
            "escalation_recommended": True,
            "contract_version": "trinity.spot.v1alpha1",
        },
        "spot_review_outcome": {
            "company_id": "company-1",
            "cycle_id": "cycle-1",
            "run_id": "run-1",
            "row_ref": "sheet1:42",
            "selected_candidate_key": "review",
            "disposition": "CORRECTED",
            "final_label": "Structural Antisemitism",
            "occurred_at": datetime(2026, 5, 9, 12, 1, tzinfo=UTC).isoformat(),
            "reviewer_notes": "Human confirmed the higher-risk interpretation.",
            "metadata": {},
            "contract_version": "trinity.spot.v1alpha1",
        },
        "labels": {"bundle_type": "spot-review-policy-learning"},
        "contract_version": "trinity.spot.v1alpha1",
    }


def test_load_trinity_spot_training_bundle_accepts_valid_bundle(tmp_path: Path) -> None:
    fixture = tmp_path / "spot_bundle.json"
    fixture.write_text(json.dumps({"bundle": _bundle_payload()}, indent=2), encoding="utf-8")

    bundle = load_trinity_spot_training_bundle(fixture)

    assert bundle.bundle_type == "spot-review-policy-learning"
    assert bundle.spot_review_outcome.final_label == "Structural Antisemitism"
    assert bundle.spot_reasoning_result.review_required is True


def test_load_trinity_spot_training_bundle_rejects_invalid_contract_version(
    tmp_path: Path,
) -> None:
    payload = _bundle_payload()
    payload["contract_version"] = "wrong.v1"
    fixture = tmp_path / "spot_bundle.json"
    fixture.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    with pytest.raises(ValueError, match="contract_version"):
        load_trinity_spot_training_bundle(fixture)
