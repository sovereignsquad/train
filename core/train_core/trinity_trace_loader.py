from __future__ import annotations

import json
from pathlib import Path

from train_core.schemas import (
    TrinityReplyTraceRecord,
    TrinitySpotTrainingBundleRecord,
    TrinityTrainingBundleRecord,
)


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


def load_trinity_training_bundle(path: str | Path) -> TrinityTrainingBundleRecord:
    bundle_path = Path(path)
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    if "bundle" in payload and isinstance(payload["bundle"], dict):
        payload = payload["bundle"]
    return TrinityTrainingBundleRecord.model_validate(payload)


def load_trinity_spot_training_bundle(path: str | Path) -> TrinitySpotTrainingBundleRecord:
    bundle_path = Path(path)
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    if "bundle" in payload and isinstance(payload["bundle"], dict):
        payload = payload["bundle"]
    return TrinitySpotTrainingBundleRecord.model_validate(payload)


def load_trinity_training_bundles(directory: str | Path) -> list[TrinityTrainingBundleRecord]:
    root = Path(directory)
    bundles = [
        load_trinity_training_bundle(path)
        for path in sorted(root.glob("*.json"))
    ]
    return bundles
