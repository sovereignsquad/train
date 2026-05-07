from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

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
            "messages": (
                {
                    "message_id": "msg-1",
                    "role": "CONTACT",
                    "text": "Can you send the update?",
                    "occurred_at": datetime(2026, 5, 3, 11, 58, tzinfo=UTC).isoformat(),
                    "channel": "linkedin",
                    "source": "linkedin",
                    "handle": "linkedin://alice",
                },
            ),
            "context_snippets": (
                {
                    "source": "vector-store",
                    "path": "snippet://alice/1",
                    "text": "Alice asked for the Q2 pricing table.",
                },
            ),
            "golden_examples": (),
            "metadata": {"source_product": "reply"},
            "contract_version": "trinity.reply.v1alpha1",
        },
        "evidence_units": (
            {
                "company_id": "company-1",
                "evidence_id": "evidence-1",
                "source_type": "TRANSCRIPT",
                "source_ref": {
                    "external_id": "msg-1",
                    "locator": "linkedin://alice",
                    "version": datetime(2026, 5, 3, 11, 58, tzinfo=UTC).isoformat(),
                },
                "content_raw": "Can you send the update?",
                "content_canonical": "Can you send the update?",
                "content_hash": "abc123",
                "metadata": {"channel": "linkedin"},
                "topic_hints": ("update",),
                "created_at": datetime(2026, 5, 3, 11, 59, tzinfo=UTC).isoformat(),
                "updated_at": datetime(2026, 5, 3, 11, 59, tzinfo=UTC).isoformat(),
            },
        ),
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
                    "draft_text": "Thanks Alice. I can send the update today.",
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
            "disposition": "SENT_AS_IS",
            "occurred_at": datetime(2026, 5, 3, 12, 1, tzinfo=UTC).isoformat(),
            "candidate_id": "candidate-1",
            "original_draft_text": "Thanks Alice. I can send the update today.",
            "final_text": "Thanks Alice. I can send the update today.",
            "edit_distance": 0.0,
            "latency_ms": 1000,
            "send_result": "ok",
            "notes": "fixture",
        },
        "labels": {"slice": "tone"},
        "contract_version": "trinity.reply.v1alpha1",
    }


def test_load_trinity_training_bundle_accepts_valid_bundle(tmp_path: Path) -> None:
    fixture = tmp_path / "bundle.json"
    fixture.write_text(json.dumps({"bundle": _bundle_payload()}, indent=2), encoding="utf-8")

    bundle = load_trinity_training_bundle(fixture)

    assert bundle.bundle_type == "tone-learning"
    assert bundle.ranked_draft_set.accepted_artifact_version.artifact_key == "reply_ranker_policy"
    assert bundle.selected_candidate_id == "candidate-1"


def test_load_trinity_training_bundle_rejects_invalid_contract_version(tmp_path: Path) -> None:
    payload = _bundle_payload()
    payload["contract_version"] = "wrong.v1"
    fixture = tmp_path / "bundle.json"
    fixture.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    with pytest.raises(ValueError, match="contract_version"):
        load_trinity_training_bundle(fixture)


def test_load_trinity_training_bundle_rejects_missing_selected_candidate(tmp_path: Path) -> None:
    payload = _bundle_payload()
    payload["selected_candidate_id"] = "candidate-missing"
    fixture = tmp_path / "bundle.json"
    fixture.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    with pytest.raises(ValueError, match="selected_candidate_id"):
        load_trinity_training_bundle(fixture)
