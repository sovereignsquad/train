from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from train_core.trinity_trace_loader import load_trinity_reply_trace


def build_fixture_from_trace(
    trace_path: str | Path,
    *,
    comparison_log_path: str | Path | None = None,
) -> dict[str, Any]:
    record = load_trinity_reply_trace(trace_path)
    fixture: dict[str, Any] = {
        "trace": record.model_dump(mode="json"),
    }
    if comparison_log_path is not None:
        comparison = latest_shadow_comparison(comparison_log_path, cycle_id=record.cycle_id)
        if comparison is not None:
            fixture["shadow_comparison"] = comparison
    return fixture


def latest_shadow_comparison(
    comparison_log_path: str | Path,
    *,
    cycle_id: str,
) -> dict[str, Any] | None:
    path = Path(comparison_log_path)
    if not path.exists():
        return None
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for row in reversed(rows):
        if str(row.get("cycleId") or "") == str(cycle_id):
            return row
    return None


def write_fixture(
    output_path: str | Path,
    *,
    trace_path: str | Path,
    comparison_log_path: str | Path | None = None,
) -> Path:
    payload = build_fixture_from_trace(
        trace_path,
        comparison_log_path=comparison_log_path,
    )
    destination = Path(output_path)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return destination
