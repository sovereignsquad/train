from __future__ import annotations

import json
from pathlib import Path

from train_core.schemas import TrinityReplyTraceRecord


def load_trinity_reply_trace(path: str | Path) -> TrinityReplyTraceRecord:
    trace_path = Path(path)
    payload = json.loads(trace_path.read_text(encoding="utf-8"))
    if "trace" in payload and isinstance(payload["trace"], dict):
        payload = payload["trace"]
    return TrinityReplyTraceRecord.model_validate(payload)


def load_trinity_reply_traces(directory: str | Path) -> list[TrinityReplyTraceRecord]:
    root = Path(directory)
    traces = [
        load_trinity_reply_trace(path)
        for path in sorted(root.glob("*.json"))
    ]
    return traces
