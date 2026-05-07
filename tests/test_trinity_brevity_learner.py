from __future__ import annotations

from datetime import UTC, datetime

import pytest

from train_core.schemas import TrinityTrainingBundleRecord
from train_core.trinity_brevity_learner import learn_reply_brevity_policy


def _bundle(
    *,
    company_id: str = "company-1",
    channel: str = "linkedin",
    bundle_type: str = "brevity-learning",
    final_text: str,
) -> TrinityTrainingBundleRecord:
    return TrinityTrainingBundleRecord.model_validate(
        {
            "bundle_id": f"bundle-{hash((channel, bundle_type, final_text)) & 0xffff}",
            "bundle_type": bundle_type,
            "exported_at": datetime(2026, 5, 3, 12, 0, tzinfo=UTC).isoformat(),
            "thread_snapshot": {
                "company_id": company_id,
                "thread_ref": f"reply:{channel}:alice",
                "channel": channel,
                "contact_handle": f"{channel}://alice",
                "latest_inbound_text": "Can you send the update?",
                "requested_at": datetime(2026, 5, 3, 11, 59, tzinfo=UTC).isoformat(),
                "messages": (
                    {
                        "message_id": "msg-1",
                        "role": "CONTACT",
                        "text": "Can you send the update?",
                        "occurred_at": datetime(2026, 5, 3, 11, 58, tzinfo=UTC).isoformat(),
                        "channel": channel,
                        "source": channel,
                        "handle": f"{channel}://alice",
                    },
                ),
                "context_snippets": (),
                "golden_examples": (),
                "metadata": {"source_product": "reply"},
                "contract_version": "trinity.reply.v1alpha1",
            },
            "evidence_units": (
                {
                    "company_id": company_id,
                    "evidence_id": "evidence-1",
                    "source_type": "TRANSCRIPT",
                    "source_ref": {
                        "external_id": "msg-1",
                        "locator": f"{channel}://alice",
                        "version": datetime(2026, 5, 3, 11, 58, tzinfo=UTC).isoformat(),
                    },
                    "content_raw": "Can you send the update?",
                    "content_canonical": "Can you send the update?",
                    "content_hash": "abc123",
                    "metadata": {"channel": channel},
                    "topic_hints": ("update",),
                    "created_at": datetime(2026, 5, 3, 11, 59, tzinfo=UTC).isoformat(),
                    "updated_at": datetime(2026, 5, 3, 11, 59, tzinfo=UTC).isoformat(),
                },
            ),
            "ranked_draft_set": {
                "cycle_id": "cycle-1",
                "thread_ref": f"reply:{channel}:alice",
                "channel": channel,
                "generated_at": datetime(2026, 5, 3, 12, 0, tzinfo=UTC).isoformat(),
                "drafts": (
                    {
                        "company_id": company_id,
                        "candidate_id": "candidate-1",
                        "thread_ref": f"reply:{channel}:alice",
                        "recipient_handle": f"{channel}://alice",
                        "channel": channel,
                        "rank": 1,
                        "draft_text": "Longer draft text that might get shortened by the operator.",
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
                "company_id": company_id,
                "cycle_id": "cycle-1",
                "thread_ref": f"reply:{channel}:alice",
                "channel": channel,
                "disposition": "EDITED_THEN_SENT",
                "occurred_at": datetime(2026, 5, 3, 12, 1, tzinfo=UTC).isoformat(),
                "candidate_id": "candidate-1",
                "original_draft_text": "Longer draft text that might get shortened by the operator.",
                "final_text": final_text,
                "edit_distance": 0.2,
                "latency_ms": 1000,
                "send_result": "ok",
                "notes": "fixture",
            },
            "labels": {"slice": "brevity"},
            "contract_version": "trinity.reply.v1alpha1",
        }
    )


def test_learn_reply_brevity_policy_returns_company_scoped_policy() -> None:
    proposal = learn_reply_brevity_policy(
        [
            _bundle(final_text="Thanks Alice. Sending today."),
            _bundle(final_text="Thanks Alice. Sharing now."),
        ]
    )

    assert proposal.scope_kind == "company"
    assert proposal.scope_value == "company-1"
    assert proposal.brevity_preferences.target_length == "short"
    assert proposal.brevity_preferences.max_sentences == 2
    assert proposal.brevity_preferences.max_chars == 80
    assert proposal.brevity_preferences.prefer_single_paragraph is True
    assert proposal.contract_version == "trinity.reply.v1alpha1"


def test_learn_reply_brevity_policy_uses_channel_scope_for_mixed_companies() -> None:
    proposal = learn_reply_brevity_policy(
        [
            _bundle(company_id="company-1", channel="linkedin", final_text="Thanks Alice. Sending today."),
            _bundle(company_id="company-2", channel="linkedin", final_text="Thanks Alice. Sending the update over today."),
        ]
    )

    assert proposal.scope_kind == "channel"
    assert proposal.scope_value == "linkedin"


def test_learn_reply_brevity_policy_uses_global_scope_for_mixed_channels() -> None:
    proposal = learn_reply_brevity_policy(
        [
            _bundle(company_id="company-1", channel="linkedin", final_text="Thanks Alice. Sending today."),
            _bundle(company_id="company-2", channel="email", final_text="Thanks Alice. Sending the update over today."),
        ]
    )

    assert proposal.scope_kind == "global"
    assert proposal.scope_value is None


def test_learn_reply_brevity_policy_rejects_non_brevity_bundles() -> None:
    with pytest.raises(ValueError, match="brevity-learning"):
        learn_reply_brevity_policy(
            [_bundle(bundle_type="tone-learning", final_text="Thanks Alice.")]
        )
