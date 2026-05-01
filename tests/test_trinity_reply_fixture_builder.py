from __future__ import annotations

import json
from pathlib import Path

from train_core.trinity_reply_fixture_builder import (
    build_fixture_from_trace,
    latest_shadow_comparison,
)


def test_build_fixture_from_trace_reads_reference_fixture(tmp_path: Path) -> None:
    trace_path = tmp_path / "trace.json"
    shadow_log_path = tmp_path / "shadow.jsonl"
    trace_path.write_text(
        json.dumps(
            {
                "contract_version": "trinity.reply.v1alpha1",
                "cycle_id": "3d4e69ab-ef1b-4e27-9dd0-7c18b5ab95dd",
                "exported_at": "2026-05-01T12:00:00+00:00",
                "snapshot_hash": "fixture-snapshot-hash",
                "frontier_candidate_ids": [
                    "9775975b-b154-4f86-b5bc-57debd5d4a2c",
                    "4663eaea-22f9-4d7c-b26d-aed9f048eb4f",
                    "0b1578fb-f6cd-4372-b7a5-87f246f3944b",
                ],
                "feedback_events": [
                    {
                        "candidate_id": "9775975b-b154-4f86-b5bc-57debd5d4a2c",
                        "channel": "linkedin",
                        "company_id": "7b801f2b-0b8c-5729-bcdc-44a54bf93f57",
                        "cycle_id": "3d4e69ab-ef1b-4e27-9dd0-7c18b5ab95dd",
                        "disposition": "SENT_AS_IS",
                        "occurred_at": "2026-05-01T12:01:48+00:00",
                        "thread_ref": "reply:linkedin:alice",
                    }
                ],
                "model_routes": {
                    "evaluator": "deterministic:v0",
                    "generator": "deterministic:v0",
                    "refiner": "deterministic:v0",
                },
                "accepted_artifact_version": {
                    "accepted_at": "2026-05-01T12:00:00+00:00",
                    "artifact_key": "reply_ranker_policy",
                    "source_project": "trinity",
                    "version": "reply_ranker_policy.v0",
                },
            }
        ),
        encoding="utf-8",
    )
    shadow_log_path.write_text(
        json.dumps(
            {
                "cycleId": "3d4e69ab-ef1b-4e27-9dd0-7c18b5ab95dd",
                "comparison": {"sameText": False, "overlapRatio": 0.42},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    fixture = build_fixture_from_trace(trace_path, comparison_log_path=shadow_log_path)

    assert fixture["trace"]["cycle_id"] == "3d4e69ab-ef1b-4e27-9dd0-7c18b5ab95dd"
    assert fixture["shadow_comparison"]["comparison"]["overlapRatio"] == 0.42


def test_latest_shadow_comparison_returns_none_when_missing(tmp_path: Path) -> None:
    path = tmp_path / "missing.jsonl"
    assert latest_shadow_comparison(path, cycle_id="cycle-1") is None
