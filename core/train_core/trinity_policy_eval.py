from __future__ import annotations

from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

from pydantic import BaseModel, Field

from train_core.comparison import (
    StandardComparisonReport,
    StandardComparisonRow,
    build_standard_comparison_report,
)
from train_core.models import MetricDirection
from train_core.schemas import ReplyBehaviorPolicyProposal, TrinityTrainingBundleRecord


class ReplyPolicyEvalReport(BaseModel):
    report_id: str = Field(min_length=1, max_length=160)
    generated_at: datetime
    learner_kind: str = Field(min_length=1, max_length=80)
    bundle_count: int = Field(ge=1)
    incumbent_artifact_key: str = Field(min_length=1, max_length=120)
    incumbent_version: str = Field(min_length=1, max_length=120)
    candidate_artifact_key: str = Field(min_length=1, max_length=120)
    candidate_version: str = Field(min_length=1, max_length=160)
    scope_kind: str = Field(min_length=1, max_length=40)
    scope_value: str | None = None
    disposition_counts: dict[str, int]
    average_edit_distance: float = Field(ge=0.0, le=1.0)
    average_final_chars: float = Field(ge=0.0)
    average_final_sentences: float = Field(ge=0.0)
    replay_ready: bool = True
    summary: str = Field(min_length=1)


def build_reply_policy_eval_report(
    bundles: list[TrinityTrainingBundleRecord],
    proposal: ReplyBehaviorPolicyProposal,
    *,
    learner_kind: str,
    generated_at: datetime | None = None,
) -> ReplyPolicyEvalReport:
    if not bundles:
        raise ValueError("At least one training bundle is required.")

    ordered = sorted(bundles, key=lambda bundle: (bundle.exported_at, bundle.bundle_id))
    incumbent = ordered[-1].ranked_draft_set.accepted_artifact_version
    final_texts = [_resolved_final_text(bundle) for bundle in ordered]
    disposition_counts = Counter(bundle.draft_outcome_event.disposition for bundle in ordered)
    bundle_count = len(ordered)
    average_edit_distance = round(
        sum(bundle.draft_outcome_event.edit_distance or 0.0 for bundle in ordered) / bundle_count,
        6,
    )
    average_final_chars = round(sum(len(text) for text in final_texts) / bundle_count, 2)
    average_final_sentences = round(
        sum(_sentence_count(text) for text in final_texts) / bundle_count,
        2,
    )
    created = generated_at or max(bundle.exported_at for bundle in ordered)
    report_id = f"{proposal.version}.eval"

    return ReplyPolicyEvalReport(
        report_id=report_id,
        generated_at=created,
        learner_kind=learner_kind,
        bundle_count=bundle_count,
        incumbent_artifact_key=incumbent.artifact_key,
        incumbent_version=incumbent.version,
        candidate_artifact_key=proposal.artifact_key,
        candidate_version=proposal.version,
        scope_kind=proposal.scope_kind,
        scope_value=proposal.scope_value,
        disposition_counts=dict(disposition_counts),
        average_edit_distance=average_edit_distance,
        average_final_chars=average_final_chars,
        average_final_sentences=average_final_sentences,
        replay_ready=True,
        summary=(
            f"{learner_kind} proposal {proposal.version} evaluated on {bundle_count} bundle(s) "
            f"against incumbent {incumbent.version}."
        ),
    )


def load_reply_behavior_policy(path: str | Path) -> ReplyBehaviorPolicyProposal:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return ReplyBehaviorPolicyProposal.model_validate(payload)


def build_reply_policy_comparison_report(
    bundles: list[TrinityTrainingBundleRecord],
    candidate: ReplyBehaviorPolicyProposal,
    *,
    learner_kind: str,
    baseline: ReplyBehaviorPolicyProposal | None = None,
    incumbent: ReplyBehaviorPolicyProposal | None = None,
    generated_at: datetime | None = None,
) -> StandardComparisonReport:
    if not bundles:
        raise ValueError("At least one training bundle is required.")

    rows: list[StandardComparisonRow] = []
    if baseline is not None:
        _validate_comparable_policy(baseline, candidate)
        rows.append(_policy_row("baseline", baseline, bundles, learner_kind))
    if incumbent is not None:
        _validate_comparable_policy(incumbent, candidate)
        rows.append(_policy_row("incumbent", incumbent, bundles, learner_kind))
    else:
        artifact = sorted(bundles, key=lambda bundle: (bundle.exported_at, bundle.bundle_id))[-1].ranked_draft_set.accepted_artifact_version
        rows.append(
            StandardComparisonRow(
                label="incumbent",
                artifact_key=artifact.artifact_key,
                version=artifact.version,
                score=None,
                status="metadata_only",
                notes="Incumbent artifact content was not provided for corpus replay scoring.",
            )
        )
    rows.append(_policy_row("candidate", candidate, bundles, learner_kind))
    created = generated_at or max(bundle.exported_at for bundle in bundles)
    corpus_fingerprint = _bundle_corpus_fingerprint(bundles)
    return build_standard_comparison_report(
        report_id=f"{candidate.version}.comparison",
        generated_at=created,
        evaluation_mode="fixed_replay_corpus",
        metric_name=f"{learner_kind}_policy_fit",
        metric_direction=MetricDirection.MAXIMIZE,
        sample_count=len(bundles),
        corpus_fingerprint=corpus_fingerprint,
        rows=rows,
        summary=(
            f"Compared {learner_kind} policy artifacts on {len(bundles)} fixed bundle(s) "
            "under the same replay corpus."
        ),
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
    segments = [part for part in re.split(r"[.!?]+\s*", text.strip()) if part.strip()]
    return max(1, len(segments))


def _policy_row(
    label: str,
    policy: ReplyBehaviorPolicyProposal,
    bundles: list[TrinityTrainingBundleRecord],
    learner_kind: str,
) -> StandardComparisonRow:
    score = score_reply_policy_against_bundles(policy, bundles, learner_kind=learner_kind)
    return StandardComparisonRow(
        label=label,
        artifact_key=policy.artifact_key,
        version=policy.version,
        score=score,
        status="evaluated",
        notes=f"Scored on fixed bundle corpus for {learner_kind}.",
    )


def _validate_comparable_policy(
    policy: ReplyBehaviorPolicyProposal,
    candidate: ReplyBehaviorPolicyProposal,
) -> None:
    if policy.artifact_key != candidate.artifact_key:
        raise ValueError("Comparison policy artifact_key must match candidate artifact_key")
    if policy.scope_kind != candidate.scope_kind or policy.scope_value != candidate.scope_value:
        raise ValueError("Comparison policy scope must match candidate scope")
    if policy.contract_version != candidate.contract_version:
        raise ValueError("Comparison policy contract_version must match candidate contract_version")


def _bundle_corpus_fingerprint(bundles: list[TrinityTrainingBundleRecord]) -> str:
    digest_input = "|".join(
        f"{bundle.bundle_id}:{bundle.bundle_type}:{bundle.exported_at.isoformat()}"
        for bundle in sorted(bundles, key=lambda item: (item.exported_at, item.bundle_id))
    )
    return hashlib.sha1(digest_input.encode("utf-8")).hexdigest()


def score_reply_policy_against_bundles(
    policy: ReplyBehaviorPolicyProposal,
    bundles: list[TrinityTrainingBundleRecord],
    *,
    learner_kind: str,
) -> float:
    texts = [_resolved_final_text(bundle) for bundle in bundles]
    if learner_kind == "tone":
        score = _score_tone(policy, texts)
    elif learner_kind == "brevity":
        score = _score_brevity(policy, texts)
    elif learner_kind == "channel-formatting":
        score = _score_channel_formatting(policy, texts)
    else:
        raise ValueError("learner_kind is invalid")
    return round(max(0.0, min(1.0, score)), 6)


def _score_tone(policy: ReplyBehaviorPolicyProposal, texts: list[str]) -> float:
    warmth_hits = sum(1 for text in texts if re.search(r"\b(thanks?|appreciate|glad|happy|sorry)\b", text.lower()))
    contraction_hits = sum(text.count("'") for text in texts)
    warm_expected = warmth_hits >= max(1, len(texts) // 2)
    formal_observed = contraction_hits <= len(texts)
    score = 0.0
    score += 0.34 if (policy.tone_preferences.warmth == "warm") == warm_expected else 0.0
    score += 0.33 if (policy.tone_preferences.formality == "formal") == formal_observed else 0.0
    score += 0.33 if policy.tone_preferences.directness in {"direct", "balanced"} else 0.0
    return score


def _score_brevity(policy: ReplyBehaviorPolicyProposal, texts: list[str]) -> float:
    avg_chars = sum(len(text) for text in texts) / max(1, len(texts))
    avg_sentences = sum(_sentence_count(text) for text in texts) / max(1, len(texts))
    actual_single_paragraph = all("\n" not in text for text in texts)
    length_band = "short" if avg_chars <= 120 else "compact" if avg_chars <= 280 else "medium"
    score = 0.0
    score += 0.4 if policy.brevity_preferences.target_length == length_band else 0.0
    if policy.brevity_preferences.max_sentences is not None:
        score += max(0.0, 0.3 - min(0.3, abs(policy.brevity_preferences.max_sentences - avg_sentences) * 0.1))
    else:
        score += 0.15
    if policy.brevity_preferences.max_chars is not None:
        score += max(0.0, 0.2 - min(0.2, abs(policy.brevity_preferences.max_chars - avg_chars) / 500.0))
    else:
        score += 0.1
    score += 0.1 if policy.brevity_preferences.prefer_single_paragraph == actual_single_paragraph else 0.0
    return score


def _score_channel_formatting(policy: ReplyBehaviorPolicyProposal, texts: list[str]) -> float:
    starts_with_thanks = any(text.lower().startswith(("thanks", "thank")) for text in texts)
    starts_with_greeting = any(text.lower().startswith(("hi", "hello", "hey")) for text in texts)
    closing_gratitude = any(text.rstrip().lower().endswith(("thanks", "thank you")) for text in texts)
    question_close = any(text.rstrip().endswith("?") for text in texts)
    has_emoji = any(any(ord(char) > 10_000 for char in text) for text in texts)
    has_url = any(re.search(r"https?://\S+", text) for text in texts)
    has_newlines = any("\n" in text for text in texts)
    score = 0.0
    opening = policy.channel_rules.opening_style
    if starts_with_thanks and opening == "brief_acknowledgment":
        score += 0.2
    elif starts_with_greeting and opening == "greeting_first":
        score += 0.2
    elif not starts_with_thanks and not starts_with_greeting and opening == "direct_open":
        score += 0.2
    closing = policy.channel_rules.closing_style
    if closing_gratitude and closing == "gratitude_close":
        score += 0.15
    elif question_close and closing == "question_close":
        score += 0.15
    elif not closing_gratitude and not question_close and closing == "no_signoff":
        score += 0.15
    score += 0.15 if (policy.channel_rules.emoji_policy != "none") == has_emoji else 0.0
    if has_url and policy.channel_rules.url_policy in {"plain_urls", "markdown_links"}:
        score += 0.2
    elif not has_url and policy.channel_rules.url_policy == "omit_when_unused":
        score += 0.2
    if has_newlines and policy.channel_rules.newline_policy in {"single_break", "compact_blocks"}:
        score += 0.15
    elif not has_newlines and policy.channel_rules.newline_policy == "single_paragraph":
        score += 0.15
    score += 0.15
    return score
