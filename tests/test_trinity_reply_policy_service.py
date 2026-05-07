from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from train_api.main import propose_trinity_reply_policy
from train_core.trinity_tone_learner import learn_reply_tone_policy
from train_core.schemas import TrinityReplyPolicyProposalRequest
from train_core.trinity_reply_policy_service import propose_reply_policy_from_bundle_files
from train_core.trinity_trace_loader import load_trinity_training_bundle


def _bundle_payload() -> dict[str, object]:
    return {
        "bundle_id": "bundle-1",
        "bundle_type": "tone-learning",
        "exported_at": datetime(2026, 5, 3, 12, 0, tzinfo=UTC).isoformat(),
        "thread_snapshot": {
            "company_id": "company-1",
            "thread_ref": "reply:linkedin:alice",
            "channel": "linkedin",
            "contact_handle": "linkedin://alice",
            "latest_inbound_text": "Can you send the update?",
            "requested_at": datetime(2026, 5, 3, 11, 59, tzinfo=UTC).isoformat(),
            "messages": (),
            "context_snippets": (),
            "golden_examples": (),
            "metadata": {"source_product": "reply"},
            "contract_version": "trinity.reply.v1alpha1",
        },
        "evidence_units": (),
        "ranked_draft_set": {
            "cycle_id": "cycle-1",
            "thread_ref": "reply:linkedin:alice",
            "channel": "linkedin",
            "generated_at": datetime(2026, 5, 3, 12, 0, tzinfo=UTC).isoformat(),
            "drafts": (
                {
                    "company_id": "company-1",
                    "candidate_id": "candidate-1",
                    "thread_ref": "reply:linkedin:alice",
                    "recipient_handle": "linkedin://alice",
                    "channel": "linkedin",
                    "rank": 1,
                    "draft_text": "Draft text",
                    "rationale": "Best current action.",
                    "risk_flags": (),
                    "delivery_eligible": True,
                    "scores": {
                        "impact": 8,
                        "confidence": 7,
                        "ease": 6,
                        "quality_score": 84.0,
                        "urgency_score": 80.0,
                        "freshness_score": 79.0,
                        "feedback_score": 25.0,
                    },
                    "source_evidence_ids": ("evidence-1",),
                    "candidate_type": "ACTION",
                    "contract_version": "trinity.reply.v1alpha1",
                },
            ),
            "accepted_artifact_version": {
                "artifact_key": "reply_ranker_policy",
                "version": "reply_ranker_policy.v0",
                "source_project": "trinity",
                "accepted_at": datetime(2026, 5, 3, 12, 0, tzinfo=UTC).isoformat(),
            },
            "trace_ref": "exports/cycle-1.json",
            "contract_version": "trinity.reply.v1alpha1",
        },
        "selected_candidate_id": "candidate-1",
        "draft_outcome_event": {
            "company_id": "company-1",
            "cycle_id": "cycle-1",
            "thread_ref": "reply:linkedin:alice",
            "channel": "linkedin",
            "disposition": "EDITED_THEN_SENT",
            "occurred_at": datetime(2026, 5, 3, 12, 1, tzinfo=UTC).isoformat(),
            "candidate_id": "candidate-1",
            "original_draft_text": "Draft text",
            "final_text": "Thanks Alice. I can send the update today.",
            "edit_distance": 0.2,
            "latency_ms": 1000,
            "send_result": "ok",
            "notes": "fixture",
        },
        "labels": {"slice": "tone"},
        "contract_version": "trinity.reply.v1alpha1",
    }


def test_propose_reply_policy_from_bundle_files_writes_outputs(tmp_path: Path) -> None:
    bundle_path = tmp_path / "bundle.json"
    proposal_path = tmp_path / "proposal.json"
    eval_path = tmp_path / "eval.json"
    comparison_path = tmp_path / "comparison.json"
    bundle_path.write_text(json.dumps({"bundle": _bundle_payload()}, indent=2), encoding="utf-8")

    result = propose_reply_policy_from_bundle_files(
        learner_kind="tone",
        bundle_files=[bundle_path],
        proposal_output_path=proposal_path,
        eval_output_path=eval_path,
        comparison_output_path=comparison_path,
    )

    assert result.bundle_count == 1
    assert result.proposal.scope_kind == "company"
    assert result.proposal.scope_value == "company-1"
    assert proposal_path.exists()
    assert eval_path.exists()
    assert comparison_path.exists()
    assert result.comparison_report is not None
    assert result.comparison_report["metric_name"] == "tone_policy_fit"


def test_propose_reply_policy_from_bundle_files_compares_optional_policy_artifacts(tmp_path: Path) -> None:
    bundle_path = tmp_path / "bundle.json"
    baseline_path = tmp_path / "baseline.json"
    incumbent_path = tmp_path / "incumbent.json"
    bundle_path.write_text(json.dumps({"bundle": _bundle_payload()}, indent=2), encoding="utf-8")
    bundle = load_trinity_training_bundle(bundle_path)
    learned = learn_reply_tone_policy([bundle])
    baseline = learned.model_copy(
        update={
            "version": "reply_behavior_policy.tone.baseline",
            "tone_preferences": learned.tone_preferences.model_copy(
                update={"warmth": "neutral", "formality": "medium", "directness": "balanced"}
            ),
        }
    )
    incumbent = learned.model_copy(update={"version": "reply_behavior_policy.tone.incumbent"})
    baseline_path.write_text(json.dumps(baseline.model_dump(mode="json"), indent=2), encoding="utf-8")
    incumbent_path.write_text(json.dumps(incumbent.model_dump(mode="json"), indent=2), encoding="utf-8")

    result = propose_reply_policy_from_bundle_files(
        learner_kind="tone",
        bundle_files=[bundle_path],
        baseline_policy_file=baseline_path,
        incumbent_policy_file=incumbent_path,
    )

    assert result.comparison_report is not None
    rows = result.comparison_report["rows"]
    assert [row["label"] for row in rows] == ["baseline", "incumbent", "candidate"]


def test_train_api_proposes_reply_policy_from_bundle_files(tmp_path: Path) -> None:
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps({"bundle": _bundle_payload()}, indent=2), encoding="utf-8")

    response = propose_trinity_reply_policy(
        TrinityReplyPolicyProposalRequest(
            learner_kind="tone",
            bundle_files=(str(bundle_path),),
        )
    )

    assert response.bundle_count == 1
    assert response.proposal.scope_kind == "company"
    assert response.proposal.scope_value == "company-1"
    assert response.comparison_report is not None
