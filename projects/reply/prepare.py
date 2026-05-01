from __future__ import annotations

import json
from pathlib import Path

from train_core.config import DEFAULT_STATE_DIR


PROJECT_DIR = Path(__file__).resolve().parent
LOCAL_DATA_PATH = DEFAULT_STATE_DIR / "reply" / "eval.json"
FIXTURE_PATH = PROJECT_DIR / "eval_fixture.json"


def load_examples() -> list[dict[str, str]]:
    path = LOCAL_DATA_PATH if LOCAL_DATA_PATH.exists() else FIXTURE_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_prepared() -> None:
    LOCAL_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
