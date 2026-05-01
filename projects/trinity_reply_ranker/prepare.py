from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
FIXTURE_PATH = PROJECT_ROOT / "eval_fixture.json"


def ensure_prepared() -> None:
    if not FIXTURE_PATH.exists():
        raise FileNotFoundError(f"Missing Trinity reply trace fixture: {FIXTURE_PATH}")


def load_fixture() -> dict[str, object]:
    ensure_prepared()
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
