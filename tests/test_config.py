from __future__ import annotations

from pathlib import Path

from train_core.config import Settings, get_default_state_dir


def test_default_state_dir_uses_os_owned_location(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Darwin")

    expected = Path.home() / "Library" / "Application Support" / "train"

    assert get_default_state_dir() == expected


def test_settings_support_train_models_root_override(monkeypatch, tmp_path: Path) -> None:
    models_root = tmp_path / "shared-models"
    monkeypatch.setenv("TRAIN_MODELS_ROOT", str(models_root))

    settings = Settings()

    assert settings.train_models_root == str(models_root)
