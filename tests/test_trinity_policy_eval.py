from __future__ import annotations

from datetime import UTC, datetime

from train_core.schemas import TrinityTrainingBundleRecord
from train_core.trinity_policy_eval import (
    build_reply_policy_comparison_report,
    build_reply_policy_eval_report,
)
from train_core.trinity_tone_learner import learn_reply_tone_policy


def _bundle(final_text: str) -> TrinityTrainingBundleRecord:
    return TrinityTrainingBundleRecord.model_validate(
        {
            "bundle_id": f"bundle-{hash(final_text) & 0xffff}",
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
                "final_text": final_text,
                "edit_distance": 0.2,
                "latency_ms": 1000,
                "send_result": "ok",
                "notes": "fixture",
            },
            "labels": {"slice": "tone"},
            "contract_version": "trinity.reply.v1alpha1",
        }
    )


def test_build_reply_policy_eval_report_is_replay_ready_and_versioned() -> None:
    bundles = [
        _bundle("Thanks Alice. I can send the update today."),
        _bundle("Thanks Alice. I can share the details today."),
    ]
    proposal = learn_reply_tone_policy(bundles)

    report = build_reply_policy_eval_report(
        bundles,
        proposal,
        learner_kind="tone",
    )

    assert report.bundle_count == 2
    assert report.incumbent_artifact_key == "reply_ranker_policy"
    assert report.candidate_artifact_key == "reply_behavior_policy"
    assert report.candidate_version == proposal.version
    assert report.replay_ready is True
    assert report.average_edit_distance == 0.2


def test_build_reply_policy_comparison_report_compares_fixed_rows() -> None:
    bundles = [
        _bundle("Thanks Alice. I can send the update today."),
        _bundle("Thanks Alice. I can share the details today."),
    ]
    candidate = learn_reply_tone_policy(bundles)
    baseline = candidate.model_copy(
        update={
            "version": "reply_behavior_policy.tone.baseline",
            "tone_preferences": candidate.tone_preferences.model_copy(
                update={"warmth": "neutral", "formality": "medium", "directness": "balanced"}
            ),
        }
    )
    incumbent = candidate.model_copy(update={"version": "reply_behavior_policy.tone.incumbent"})

    report = build_reply_policy_comparison_report(
        bundles,
        candidate,
        learner_kind="tone",
        baseline=baseline,
        incumbent=incumbent,
    )

    assert report.metric_name == "tone_policy_fit"
    assert report.contract_version == "train.comparison.v1alpha1"
    assert report.evaluation_mode == "fixed_replay_corpus"
    assert len(report.corpus_fingerprint) == 40
    assert len(report.rows) == 3
    assert report.rows[-1].label == "candidate"
    assert report.rows[-1].score is not None
    assert report.rows[0].label == "baseline"
    assert report.deltas[0].from_label == "baseline"
    assert report.deltas[0].to_label == "candidate"
    assert report.table_markdown.startswith("| Label | Artifact |")


def test_build_reply_policy_comparison_report_rejects_scope_mismatch() -> None:
    bundles = [_bundle("Thanks Alice. I can send the update today.")]
    candidate = learn_reply_tone_policy(bundles)
    mismatched = candidate.model_copy(
        update={"version": "reply_behavior_policy.tone.global", "scope_kind": "global", "scope_value": None}
    )

    try:
        build_reply_policy_comparison_report(
            bundles,
            candidate,
            learner_kind="tone",
            baseline=mismatched,
        )
    except ValueError as exc:
        assert "scope" in str(exc)
    else:
        raise AssertionError("Expected mismatched scope to fail comparison.")


def test_build_reply_policy_comparison_report_rejects_contract_mismatch() -> None:
    bundles = [_bundle("Thanks Alice. I can send the update today.")]
    candidate = learn_reply_tone_policy(bundles)
    mismatched = candidate.model_copy(
        update={"version": "reply_behavior_policy.tone.other-contract", "contract_version": "trinity.reply.v9"}
    )

    try:
        build_reply_policy_comparison_report(
            bundles,
            candidate,
            learner_kind="tone",
            baseline=mismatched,
        )
    except ValueError as exc:
        assert "contract_version" in str(exc)
    else:
        raise AssertionError("Expected mismatched contract_version to fail comparison.")


def test_build_reply_policy_comparison_report_has_stable_corpus_fingerprint_for_same_bundles() -> None:
    first = _bundle("Thanks Alice. I can send the update today.")
    second = _bundle("Thanks Alice. I can share the details today.")
    candidate = learn_reply_tone_policy([first, second])

    report_a = build_reply_policy_comparison_report(
        [first, second],
        candidate,
        learner_kind="tone",
    )
    report_b = build_reply_policy_comparison_report(
        [second, first],
        candidate,
        learner_kind="tone",
    )

    assert report_a.corpus_fingerprint == report_b.corpus_fingerprint
