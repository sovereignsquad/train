from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from train_api.main import propose_trinity_reply_policy
from train_core.cli import main as train_cli_main
from train_core.trinity_tone_learner import learn_reply_tone_policy
from train_core.schemas import TrinityReplyPolicyPromotionPackage, TrinityReplyPolicyProposalRequest
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
    assert result.comparison_report["evaluation_mode"] == "fixed_replay_corpus"
    assert result.comparison_report["corpus_fingerprint"]


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


def test_train_cli_can_render_matrix_output(tmp_path: Path, capsys) -> None:
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps({"bundle": _bundle_payload()}, indent=2), encoding="utf-8")

    exit_code = train_cli_main(
        [
            "propose-reply-policy",
            "--learner-kind",
            "tone",
            "--bundle-file",
            str(bundle_path),
            "--output-format",
            "matrix",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "| Label | Artifact | Version | Score | Status | Notes |" in captured.out
    assert "candidate" in captured.out


def test_reply_policy_request_rejects_duplicate_bundle_files() -> None:
    try:
        TrinityReplyPolicyProposalRequest(
            learner_kind="tone",
            bundle_files=("same.json", "same.json"),
        )
    except ValueError as exc:
        assert "duplicates" in str(exc)
    else:
        raise AssertionError("Expected duplicate bundle files to fail validation.")


def test_promotion_package_requires_absolute_paths() -> None:
    package = TrinityReplyPolicyPromotionPackage(
        component_key="reply.tone",
        accepted_project_key="reply",
        accepted_run_id=7,
        accepted_metric=0.91,
        accepted_artifact_version="reply_behavior_policy.tone.company-1.v1",
        proposal_artifact_path="/tmp/proposal.json",
        comparison_report_path="/tmp/comparison.json",
        contract_version="trinity.reply.v1alpha1",
        scope_kind="company",
        scope_value="company-1",
        promotion_notes="fixture",
    )

    assert package.scope_kind == "company"

    try:
        TrinityReplyPolicyPromotionPackage(
            component_key="reply.tone",
            accepted_project_key="reply",
            accepted_artifact_version="reply_behavior_policy.tone.company-1.v1",
            proposal_artifact_path="relative/proposal.json",
            contract_version="trinity.reply.v1alpha1",
            scope_kind="company",
            scope_value="company-1",
        )
    except ValueError as exc:
        assert "absolute" in str(exc)
    else:
        raise AssertionError("Expected relative proposal path to fail validation.")
