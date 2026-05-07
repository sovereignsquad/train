from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from train_core.schemas import TrinityReplyPolicyProposalRead
from train_core.trinity_brevity_learner import learn_reply_brevity_policy
from train_core.trinity_channel_formatting_learner import (
    learn_reply_channel_formatting_policy,
)
from train_core.trinity_policy_eval import (
    build_reply_policy_comparison_report,
    build_reply_policy_eval_report,
    load_reply_behavior_policy,
)
from train_core.trinity_tone_learner import learn_reply_tone_policy
from train_core.trinity_trace_loader import load_trinity_training_bundle


def propose_reply_policy_from_bundle_files(
    *,
    learner_kind: str,
    bundle_files: list[str | Path],
    baseline_policy_file: str | Path | None = None,
    incumbent_policy_file: str | Path | None = None,
    proposal_output_path: str | Path | None = None,
    eval_output_path: str | Path | None = None,
    comparison_output_path: str | Path | None = None,
) -> TrinityReplyPolicyProposalRead:
    if not bundle_files:
        raise ValueError("At least one training bundle file is required.")

    bundles = [load_trinity_training_bundle(path) for path in bundle_files]
    proposal = _learn_policy(learner_kind, bundles)
    eval_report = build_reply_policy_eval_report(
        bundles,
        proposal,
        learner_kind=learner_kind,
    )
    baseline_policy = load_reply_behavior_policy(baseline_policy_file) if baseline_policy_file is not None else None
    incumbent_policy = load_reply_behavior_policy(incumbent_policy_file) if incumbent_policy_file is not None else None
    comparison_report = build_reply_policy_comparison_report(
        bundles,
        proposal,
        learner_kind=learner_kind,
        baseline=baseline_policy,
        incumbent=incumbent_policy,
    )

    proposal_path = _write_json_file(proposal_output_path, proposal.model_dump(mode="json"))
    eval_path = _write_json_file(eval_output_path, eval_report.model_dump(mode="json"))
    comparison_path = _write_json_file(
        comparison_output_path,
        comparison_report.model_dump(mode="json"),
    )
    return TrinityReplyPolicyProposalRead(
        learner_kind=learner_kind,
        bundle_count=len(bundles),
        proposal=proposal,
        eval_report=eval_report.model_dump(mode="json"),
        comparison_report=comparison_report.model_dump(mode="json"),
        proposal_path=str(proposal_path) if proposal_path is not None else None,
        eval_output_path=str(eval_path) if eval_path is not None else None,
        comparison_output_path=str(comparison_path) if comparison_path is not None else None,
    )


def _learn_policy(learner_kind: str, bundles: list[Any]):
    if learner_kind == "tone":
        return learn_reply_tone_policy(bundles)
    if learner_kind == "brevity":
        return learn_reply_brevity_policy(bundles)
    if learner_kind == "channel-formatting":
        return learn_reply_channel_formatting_policy(bundles)
    raise ValueError("learner_kind is invalid")


def _write_json_file(path: str | Path | None, payload: dict[str, Any]) -> Path | None:
    if path is None:
        return None
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return output_path
