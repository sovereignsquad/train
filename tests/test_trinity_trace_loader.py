from __future__ import annotations

from pathlib import Path

from train_core.trinity_trace_loader import load_trinity_reply_trace


def test_load_trinity_reply_trace_reads_reference_fixture() -> None:
    fixture = Path("projects/trinity_reply_ranker/eval_fixture.json")
    record = load_trinity_reply_trace(fixture)

    assert record.contract_version == "trinity.reply.v1alpha1"
    assert record.accepted_artifact_version.artifact_key == "reply_ranker_policy"
    assert record.feedback_events[0].disposition == "SENT_AS_IS"
