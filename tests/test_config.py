from __future__ import annotations

from pathlib import Path

from train_core.config import get_default_state_dir


def test_default_state_dir_uses_os_owned_location(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Darwin")

    expected = Path.home() / "Library" / "Application Support" / "train"

    assert get_default_state_dir() == expected
