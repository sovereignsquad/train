from __future__ import annotations

import hashlib
import re
from collections import Counter
from datetime import UTC, datetime

from train_core.schemas import (
    ReplyBehaviorPolicyProposal,
    ReplyBrevityPreferencesProposal,
    ReplyChannelRulesProposal,
    ReplyTonePreferencesProposal,
    TrinityTrainingBundleRecord,
)
from train_core.trinity_scope import derive_reply_policy_scope


WARM_TOKENS = {"thanks", "thank", "appreciate", "glad", "happy", "sorry"}
SOFTENING_TOKENS = {"maybe", "might", "could", "just", "wanted", "perhaps"}
CASUAL_TOKENS = {"hey", "hi", "ok", "okay", "yep", "lol"}
FORBIDDEN_TONE_WEIGHTS = {
    "pushy": 0,
    "defensive": 0,
    "robotic": 0,
}


def learn_reply_tone_policy(
    bundles: list[TrinityTrainingBundleRecord],
    *,
    created_at: datetime | None = None,
) -> ReplyBehaviorPolicyProposal:
    if not bundles:
        raise ValueError("At least one training bundle is required.")
    for bundle in bundles:
        if bundle.bundle_type != "tone-learning":
            raise ValueError("Tone learner accepts only tone-learning bundles.")

    ordered = sorted(bundles, key=lambda bundle: (bundle.exported_at, bundle.bundle_id))
    scope_kind, scope_value = derive_reply_policy_scope(ordered)

    final_texts = [_resolved_final_text(bundle) for bundle in ordered]
    warmth = _infer_warmth(final_texts)
    directness = _infer_directness(final_texts)
    formality = _infer_formality(final_texts)
    target_tone = _infer_target_tone(warmth=warmth, directness=directness, formality=formality)
    created = created_at or max(bundle.exported_at for bundle in ordered)
    contract_version = ordered[-1].contract_version

    digest_source = "|".join(bundle.bundle_id for bundle in ordered)
    digest = hashlib.sha1(digest_source.encode("utf-8")).hexdigest()[:12]
    version_scope = scope_value or "global"
    version = (
        f"reply_behavior_policy.tone.{version_scope}."
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
            target_tone=target_tone,
            formality=formality,
            warmth=warmth,
            directness=directness,
            forbidden_tones=_infer_forbidden_tones(final_texts),
        ),
        brevity_preferences=ReplyBrevityPreferencesProposal(
            target_length="compact",
            max_sentences=3,
            max_chars=280,
            prefer_single_paragraph=True,
        ),
        channel_rules=ReplyChannelRulesProposal(
            opening_style=_infer_opening_style(final_texts),
            closing_style="no_signoff",
            emoji_policy="none",
            url_policy="plain_urls",
            attachment_reference_policy="mention_if_used",
            newline_policy="single_paragraph",
        ),
        notes=(
            f"Learned from {len(ordered)} tone-learning bundle(s) for "
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


def _infer_warmth(texts: list[str]) -> str:
    token_count = sum(_count_matching_tokens(text, WARM_TOKENS) for text in texts)
    if token_count >= max(1, len(texts)):
        return "warm"
    return "neutral"


def _infer_directness(texts: list[str]) -> str:
    softening = sum(_count_matching_tokens(text, SOFTENING_TOKENS) for text in texts)
    if softening >= len(texts):
        return "balanced"
    return "direct"


def _infer_formality(texts: list[str]) -> str:
    casual = sum(_count_matching_tokens(text, CASUAL_TOKENS) for text in texts)
    contractions = sum(text.count("'") for text in texts)
    if casual or contractions > len(texts):
        return "medium"
    return "formal"


def _infer_target_tone(*, warmth: str, directness: str, formality: str) -> str:
    if warmth == "warm" and directness == "direct":
        return "warm_direct"
    if formality == "formal":
        return "calm_formal"
    return "calm"


def _infer_forbidden_tones(texts: list[str]) -> tuple[str, ...]:
    counts = Counter(_normalized_token(text) for text in texts for _ in [0])
    forbidden = list(FORBIDDEN_TONE_WEIGHTS)
    if any("!" in text for text in texts):
        forbidden = [tone for tone in forbidden if tone != "pushy"]
    if counts.get("sorry", 0) > len(texts):
        forbidden = [tone for tone in forbidden if tone != "defensive"]
    return tuple(forbidden)


def _infer_opening_style(texts: list[str]) -> str:
    if any(text.lower().startswith(("thanks", "thank")) for text in texts):
        return "brief_acknowledgment"
    return "direct_open"


def _count_matching_tokens(text: str, targets: set[str]) -> int:
    tokens = {_normalized_token(token) for token in re.split(r"\s+", text.lower()) if token.strip()}
    return sum(1 for token in tokens if token in targets)


def _normalized_token(token: str) -> str:
    return re.sub(r"[^a-z]+", "", token.lower())
