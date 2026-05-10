from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from train_api.main import propose_trinity_spot_policy
from train_core.cli import main as train_cli_main
from train_core.schemas import TrinitySpotPolicyProposalRequest
from train_core.trinity_spot_policy_service import propose_spot_review_policy_from_bundle_files


def _bundle_payload(
    *,
    final_label: str = "Not Antisemitic",
    disposition: str = "CONFIRMED_NEGATIVE",
    combined_confidence: float = 0.76,
) -> dict[str, object]:
    return {
        "bundle_id": f"bundle-{hash((final_label, disposition, combined_confidence)) & 0xffff}",
        "bundle_type": "spot-review-policy-learning",
        "exported_at": datetime(2026, 5, 9, 12, 0, tzinfo=UTC).isoformat(),
        "spot_reasoning_request": {
            "company_id": "company-1",
            "run_id": "run-1",
            "row_ref": "sheet1:42",
            "language": "de",
            "message_text": "Sample row",
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
                    "candidate_key": "benign" if final_label == "Not Antisemitic" else "review",
                    "interpretation": "Sample",
                    "rationale": "Sample",
                    "threat_label_hint": final_label,
                    "review_recommended": final_label != "Not Antisemitic",
                },
            ),
            "selected_candidate_key": "benign" if final_label == "Not Antisemitic" else "review",
            "confidence_bundle": {
                "generator_confidence": combined_confidence,
                "refiner_confidence": combined_confidence,
                "evaluator_confidence": combined_confidence,
                "frontier_confidence": combined_confidence,
                "combined_confidence": combined_confidence,
                "disagreement_severity": 0.1,
            },
            "review_required": final_label != "Not Antisemitic",
            "review_reason": "fixture",
            "policy_sensitive": final_label != "Not Antisemitic",
            "automatic_disposition": (
                "auto_approve" if final_label == "Not Antisemitic" else "review_required"
            ),
            "human_override_allowed": True,
            "deeper_analysis_available": True,
            "escalation_recommended": final_label != "Not Antisemitic",
            "contract_version": "trinity.spot.v1alpha1",
        },
        "spot_review_outcome": {
            "company_id": "company-1",
            "cycle_id": "cycle-1",
            "run_id": "run-1",
            "row_ref": "sheet1:42",
            "selected_candidate_key": "benign" if final_label == "Not Antisemitic" else "review",
            "disposition": disposition,
            "final_label": final_label,
            "occurred_at": datetime(2026, 5, 9, 12, 1, tzinfo=UTC).isoformat(),
            "reviewer_notes": "fixture",
            "metadata": {},
            "contract_version": "trinity.spot.v1alpha1",
        },
        "labels": {"bundle_type": "spot-review-policy-learning"},
        "contract_version": "trinity.spot.v1alpha1",
    }


def test_propose_spot_review_policy_from_bundle_files_writes_outputs(tmp_path: Path) -> None:
    bundle_path = tmp_path / "spot_bundle.json"
    proposal_path = tmp_path / "proposal.json"
    eval_path = tmp_path / "eval.json"
    bundle_path.write_text(
        json.dumps({"bundle": _bundle_payload()}, indent=2),
        encoding="utf-8",
    )

    result = propose_spot_review_policy_from_bundle_files(
        learner_kind="review-policy",
        bundle_files=[bundle_path],
        proposal_output_path=proposal_path,
        eval_output_path=eval_path,
    )

    assert result.bundle_count == 1
    assert result.proposal.auto_approve_negative_threshold == 0.76
    assert result.proposal.scope_kind == "company"
    assert result.proposal.scope_value == "company-1"
    assert proposal_path.exists()
    assert eval_path.exists()
    assert result.eval_report["negative_count"] == 1


def test_train_api_proposes_spot_review_policy_from_bundle_files(tmp_path: Path) -> None:
    bundle_path = tmp_path / "spot_bundle.json"
    bundle_path.write_text(
        json.dumps({"bundle": _bundle_payload(final_label="Structural Antisemitism", disposition="CONFIRMED_POSITIVE", combined_confidence=0.83)}, indent=2),
        encoding="utf-8",
    )

    response = propose_trinity_spot_policy(
        TrinitySpotPolicyProposalRequest(
            learner_kind="review-policy",
            bundle_files=(str(bundle_path),),
        )
    )

    assert response.bundle_count == 1
    assert response.proposal.positive_review_required is True
    assert response.proposal.scope_kind == "company"
    assert response.eval_report["positive_count"] == 1


def test_train_cli_can_render_spot_summary_output(tmp_path: Path, capsys) -> None:
    bundle_path = tmp_path / "spot_bundle.json"
    bundle_path.write_text(
        json.dumps({"bundle": _bundle_payload()}, indent=2),
        encoding="utf-8",
    )

    exit_code = train_cli_main(
        [
            "propose-spot-review-policy",
            "--learner-kind",
            "review-policy",
            "--bundle-file",
            str(bundle_path),
            "--output-format",
            "summary",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "candidate" in captured.out
