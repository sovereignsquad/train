from __future__ import annotations

from datetime import UTC, datetime

import pytest

from train_core.schemas import TrinityTrainingBundleRecord
from train_core.trinity_channel_formatting_learner import (
    learn_reply_channel_formatting_policy,
)


def _bundle(
    *,
    company_id: str = "company-1",
    channel: str = "linkedin",
    bundle_type: str = "channel-formatting-learning",
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
                "messages": (),
                "context_snippets": (),
                "golden_examples": (),
                "metadata": {"source_product": "reply"},
                "contract_version": "trinity.reply.v1alpha1",
            },
            "evidence_units": (),
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
                "company_id": company_id,
                "cycle_id": "cycle-1",
                "thread_ref": f"reply:{channel}:alice",
                "channel": channel,
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
            "labels": {"slice": "formatting"},
            "contract_version": "trinity.reply.v1alpha1",
        }
    )


def test_learn_reply_channel_formatting_policy_returns_company_scoped_policy() -> None:
    proposal = learn_reply_channel_formatting_policy(
        [
            _bundle(final_text="Thanks Alice.\nHere's the link: https://example.com"),
            _bundle(final_text="Thanks Alice.\nAttached is the file."),
        ]
    )

    assert proposal.scope_kind == "company"
    assert proposal.scope_value == "company-1"
    assert proposal.channel_rules.opening_style == "brief_acknowledgment"
    assert proposal.channel_rules.url_policy == "plain_urls"
    assert proposal.channel_rules.attachment_reference_policy == "mention_if_used"
    assert proposal.channel_rules.newline_policy == "single_break"


def test_learn_reply_channel_formatting_policy_uses_channel_scope_for_mixed_companies() -> None:
    proposal = learn_reply_channel_formatting_policy(
        [
            _bundle(company_id="company-1", channel="linkedin", final_text="Thanks Alice."),
            _bundle(company_id="company-2", channel="linkedin", final_text="Thanks Alice."),
        ]
    )

    assert proposal.scope_kind == "channel"
    assert proposal.scope_value == "linkedin"


def test_learn_reply_channel_formatting_policy_uses_global_scope_for_mixed_channels() -> None:
    proposal = learn_reply_channel_formatting_policy(
        [
            _bundle(company_id="company-1", channel="linkedin", final_text="Thanks Alice."),
            _bundle(company_id="company-2", channel="email", final_text="Thanks Alice."),
        ]
    )

    assert proposal.scope_kind == "global"
    assert proposal.scope_value is None


def test_learn_reply_channel_formatting_policy_rejects_non_formatting_bundles() -> None:
    with pytest.raises(ValueError, match="channel-formatting-learning"):
        learn_reply_channel_formatting_policy(
            [_bundle(bundle_type="tone-learning", final_text="Thanks Alice.")]
        )
