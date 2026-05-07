from __future__ import annotations

from datetime import UTC, datetime

from train_core.schemas import TrinityTrainingBundleRecord
from train_core.trinity_scope import derive_reply_policy_scope


def _bundle(*, bundle_id: str, company_id: str, channel: str) -> TrinityTrainingBundleRecord:
    return TrinityTrainingBundleRecord.model_validate(
        {
            "bundle_id": bundle_id,
            "bundle_type": "tone-learning",
            "exported_at": datetime(2026, 5, 8, 12, 0, tzinfo=UTC).isoformat(),
            "thread_snapshot": {
                "company_id": company_id,
                "thread_ref": f"reply:{channel}:{company_id}",
                "channel": channel,
                "contact_handle": f"{channel}://{company_id}",
                "latest_inbound_text": "Can you send the update?",
                "requested_at": datetime(2026, 5, 8, 11, 59, tzinfo=UTC).isoformat(),
                "messages": (),
                "context_snippets": (),
                "golden_examples": (),
                "metadata": {"source_product": "reply"},
                "contract_version": "trinity.reply.v1alpha1",
            },
            "evidence_units": (),
            "ranked_draft_set": {
                "cycle_id": f"cycle-{bundle_id}",
                "thread_ref": f"reply:{channel}:{company_id}",
                "channel": channel,
                "generated_at": datetime(2026, 5, 8, 12, 0, tzinfo=UTC).isoformat(),
                "drafts": (
                    {
                        "company_id": company_id,
                        "candidate_id": "candidate-1",
                        "thread_ref": f"reply:{channel}:{company_id}",
                        "recipient_handle": f"{channel}://{company_id}",
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
                    "accepted_at": datetime(2026, 5, 8, 12, 0, tzinfo=UTC).isoformat(),
                },
                "trace_ref": f"exports/{bundle_id}.json",
                "contract_version": "trinity.reply.v1alpha1",
            },
            "selected_candidate_id": "candidate-1",
            "draft_outcome_event": {
                "company_id": company_id,
                "cycle_id": f"cycle-{bundle_id}",
                "thread_ref": f"reply:{channel}:{company_id}",
                "channel": channel,
                "disposition": "EDITED_THEN_SENT",
                "occurred_at": datetime(2026, 5, 8, 12, 1, tzinfo=UTC).isoformat(),
                "candidate_id": "candidate-1",
                "original_draft_text": "Draft text",
                "final_text": "Thanks. I can send the update today.",
                "edit_distance": 0.2,
                "latency_ms": 1000,
                "send_result": "ok",
                "notes": "fixture",
            },
            "labels": {"slice": "tone"},
            "contract_version": "trinity.reply.v1alpha1",
        }
    )


def test_scope_prefers_company_for_single_company_corpus() -> None:
    bundles = [
        _bundle(bundle_id="bundle-1", company_id="company-1", channel="linkedin"),
        _bundle(bundle_id="bundle-2", company_id="company-1", channel="email"),
    ]

    scope_kind, scope_value = derive_reply_policy_scope(bundles)

    assert scope_kind == "company"
    assert scope_value == "company-1"


def test_scope_uses_channel_only_when_companies_mixed_but_channel_fixed() -> None:
    bundles = [
        _bundle(bundle_id="bundle-1", company_id="company-1", channel="linkedin"),
        _bundle(bundle_id="bundle-2", company_id="company-2", channel="linkedin"),
    ]

    scope_kind, scope_value = derive_reply_policy_scope(bundles)

    assert scope_kind == "channel"
    assert scope_value == "linkedin"


def test_scope_uses_global_when_companies_and_channels_mixed() -> None:
    bundles = [
        _bundle(bundle_id="bundle-1", company_id="company-1", channel="linkedin"),
        _bundle(bundle_id="bundle-2", company_id="company-2", channel="email"),
    ]

    scope_kind, scope_value = derive_reply_policy_scope(bundles)

    assert scope_kind == "global"
    assert scope_value is None
