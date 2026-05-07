from __future__ import annotations

from train_core.schemas import TrinityTrainingBundleRecord


def derive_reply_policy_scope(
    bundles: list[TrinityTrainingBundleRecord],
) -> tuple[str, str | None]:
    if not bundles:
        raise ValueError("At least one training bundle is required.")

    normalized_companies = {
        bundle.thread_snapshot.company_id.strip().lower()
        for bundle in bundles
        if bundle.thread_snapshot.company_id.strip()
    }
    if len(normalized_companies) == 1:
        return "company", sorted(normalized_companies)[0]

    normalized_channels = {
        bundle.thread_snapshot.channel.strip().lower()
        for bundle in bundles
        if bundle.thread_snapshot.channel.strip()
    }
    if len(normalized_channels) == 1:
        return "channel", sorted(normalized_channels)[0]

    return "global", None
