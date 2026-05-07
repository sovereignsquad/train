from __future__ import annotations

import hashlib
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


def learn_reply_channel_formatting_policy(
    bundles: list[TrinityTrainingBundleRecord],
    *,
    created_at: datetime | None = None,
) -> ReplyBehaviorPolicyProposal:
    if not bundles:
        raise ValueError("At least one training bundle is required.")
    for bundle in bundles:
        if bundle.bundle_type != "channel-formatting-learning":
            raise ValueError(
                "Channel formatting learner accepts only channel-formatting-learning bundles."
            )

    ordered = sorted(bundles, key=lambda bundle: (bundle.exported_at, bundle.bundle_id))
    scope_kind, scope_value = derive_reply_policy_scope(ordered)
    created = created_at or max(bundle.exported_at for bundle in ordered)
    contract_version = ordered[-1].contract_version

    final_texts = [_resolved_final_text(bundle) for bundle in ordered]
    digest_source = "|".join(bundle.bundle_id for bundle in ordered)
    digest = hashlib.sha1(digest_source.encode("utf-8")).hexdigest()[:12]
    version_scope = scope_value or "global"
    version = (
        f"reply_behavior_policy.formatting.{version_scope}."
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
            forbidden_tones=("sloppy",),
        ),
        brevity_preferences=ReplyBrevityPreferencesProposal(
            target_length="compact",
            max_sentences=max(1, max(_sentence_count(text) for text in final_texts)),
            max_chars=max(len(text) for text in final_texts),
            prefer_single_paragraph=all("\n" not in text for text in final_texts),
        ),
        channel_rules=ReplyChannelRulesProposal(
            opening_style=_infer_opening_style(final_texts),
            closing_style=_infer_closing_style(final_texts),
            emoji_policy=_infer_emoji_policy(final_texts),
            url_policy=_infer_url_policy(final_texts),
            attachment_reference_policy=_infer_attachment_reference_policy(final_texts),
            newline_policy=_infer_newline_policy(final_texts),
        ),
        notes=(
            f"Learned from {len(ordered)} channel-formatting-learning bundle(s) for "
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


def _infer_opening_style(texts: list[str]) -> str:
    if any(text.lower().startswith(("thanks", "thank")) for text in texts):
        return "brief_acknowledgment"
    if any(text.lower().startswith(("hi", "hello", "hey")) for text in texts):
        return "greeting_first"
    return "direct_open"


def _infer_closing_style(texts: list[str]) -> str:
    if any(text.rstrip().lower().endswith(("thanks", "thank you")) for text in texts):
        return "gratitude_close"
    if any(text.rstrip().endswith("?") for text in texts):
        return "question_close"
    return "no_signoff"


def _infer_emoji_policy(texts: list[str]) -> str:
    if any(_contains_emoji(text) for text in texts):
        return "allow_sparse"
    return "none"


def _infer_url_policy(texts: list[str]) -> str:
    if any(re.search(r"\[.+\]\(https?://", text) for text in texts):
        return "markdown_links"
    if any(re.search(r"https?://\S+", text) for text in texts):
        return "plain_urls"
    return "omit_when_unused"


def _infer_attachment_reference_policy(texts: list[str]) -> str:
    attachment_markers = ("attach", "attached", "attachment", "screenshot", "file", "doc")
    if any(any(marker in text.lower() for marker in attachment_markers) for text in texts):
        return "mention_if_used"
    return "omit_when_unused"


def _infer_newline_policy(texts: list[str]) -> str:
    newline_counts = [text.count("\n") for text in texts]
    if max(newline_counts, default=0) == 0:
        return "single_paragraph"
    if any(count >= 2 for count in newline_counts):
        return "compact_blocks"
    return "single_break"


def _sentence_count(text: str) -> int:
    segments = [part for part in re.split(r"[.!?]+\s*", text.strip()) if part.strip()]
    return max(1, len(segments))


def _contains_emoji(text: str) -> bool:
    return any(ord(char) > 10_000 for char in text)
