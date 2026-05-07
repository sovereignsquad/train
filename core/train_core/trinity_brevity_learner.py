from __future__ import annotations

import hashlib
import math
import re
from datetime import UTC, datetime

from train_core.schemas import (
    ReplyBehaviorPolicyProposal,
    ReplyBrevityPreferencesProposal,
    ReplyChannelRulesProposal,
    ReplyTonePreferencesProposal,
    TrinityTrainingBundleRecord,
)
from train_core.trinity_scope import derive_reply_policy_scope


def learn_reply_brevity_policy(
    bundles: list[TrinityTrainingBundleRecord],
    *,
    created_at: datetime | None = None,
) -> ReplyBehaviorPolicyProposal:
    if not bundles:
        raise ValueError("At least one training bundle is required.")
    for bundle in bundles:
        if bundle.bundle_type != "brevity-learning":
            raise ValueError("Brevity learner accepts only brevity-learning bundles.")

    ordered = sorted(bundles, key=lambda bundle: (bundle.exported_at, bundle.bundle_id))
    scope_kind, scope_value = derive_reply_policy_scope(ordered)
    created = created_at or max(bundle.exported_at for bundle in ordered)
    contract_version = ordered[-1].contract_version

    final_texts = [_resolved_final_text(bundle) for bundle in ordered]
    max_sentences = max(1, max(_sentence_count(text) for text in final_texts))
    max_chars = _rounded_char_budget(max(len(text) for text in final_texts))
    prefer_single_paragraph = all("\n" not in text.strip() for text in final_texts)
    target_length = _infer_target_length(final_texts)

    digest_source = "|".join(bundle.bundle_id for bundle in ordered)
    digest = hashlib.sha1(digest_source.encode("utf-8")).hexdigest()[:12]
    version_scope = scope_value or "global"
    version = (
        f"reply_behavior_policy.brevity.{version_scope}."
        f"{created.astimezone(UTC).strftime('%Y%m%dT%H%M%SZ')}.{digest}"
    )

    return ReplyBehaviorPolicyProposal(
        artifact_key="reply_behavior_policy",
        version=version,
        scope_kind=scope_kind,
        scope_value=scope_value,
        created_at=created,
        source_project="train",
        tone_preferences=ReplyTonePreferencesProposal(
            target_tone="calm",
            formality="medium",
            warmth="neutral",
            directness="direct",
            forbidden_tones=("rambling",),
        ),
        brevity_preferences=ReplyBrevityPreferencesProposal(
            target_length=target_length,
            max_sentences=max_sentences,
            max_chars=max_chars,
            prefer_single_paragraph=prefer_single_paragraph,
        ),
        channel_rules=ReplyChannelRulesProposal(
            opening_style="brief_acknowledgment",
            closing_style="no_signoff",
            emoji_policy="none",
            url_policy="plain_urls",
            attachment_reference_policy="mention_if_used",
            newline_policy="single_paragraph" if prefer_single_paragraph else "compact_blocks",
        ),
        notes=(
            f"Learned from {len(ordered)} brevity-learning bundle(s) for "
            f"{scope_value or 'global'} scope."
        ),
        contract_version=contract_version,
    )


def _resolved_final_text(bundle: TrinityTrainingBundleRecord) -> str:
    final_text = (bundle.draft_outcome_event.final_text or "").strip()
    if final_text:
        return final_text
    selected_id = bundle.selected_candidate_id
    if selected_id:
        for draft in bundle.ranked_draft_set.drafts:
            if draft.candidate_id == selected_id:
                return draft.draft_text.strip()
    return bundle.thread_snapshot.latest_inbound_text.strip()


def _sentence_count(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 1
    segments = [part for part in re.split(r"[.!?]+\s*", stripped) if part.strip()]
    return max(1, len(segments))


def _rounded_char_budget(max_chars: int) -> int:
    if max_chars <= 80:
        return 80
    return int(math.ceil(max_chars / 40.0) * 40)


def _infer_target_length(texts: list[str]) -> str:
    avg_chars = sum(len(text) for text in texts) / max(len(texts), 1)
    avg_sentences = sum(_sentence_count(text) for text in texts) / max(len(texts), 1)
    if avg_chars <= 120 and avg_sentences <= 2:
        return "short"
    if avg_chars <= 280 and avg_sentences <= 3:
        return "compact"
    return "medium"
