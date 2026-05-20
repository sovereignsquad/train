from __future__ import annotations

from pathlib import Path

import pytest

from train_core.model_resolution import ModelResolutionError, get_models_root, resolve_model_ref


def test_get_models_root_uses_configured_setting(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("train_core.config.settings.train_models_root", str(tmp_path))

    assert get_models_root() == tmp_path.resolve()


def test_resolve_huggingface_model_ref_returns_passthrough() -> None:
    resolved = resolve_model_ref("mlx-community/Llama-3.2-3B-Instruct-4bit", source_kind="huggingface")

    assert resolved.source_kind == "huggingface"
    assert resolved.resolved_ref == "mlx-community/Llama-3.2-3B-Instruct-4bit"
    assert resolved.resolved_path is None


def test_resolve_local_model_ref_against_models_root(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("train_core.config.settings.train_models_root", str(tmp_path))

    resolved = resolve_model_ref("llms/chat/gemma-3-270m-it-mlx-8bit", source_kind="local-path")

    assert resolved.source_kind == "local-path"
    assert resolved.resolved_ref == "llms/chat/gemma-3-270m-it-mlx-8bit"
    assert resolved.resolved_path == str((tmp_path / "llms/chat/gemma-3-270m-it-mlx-8bit").resolve())
    assert resolved.models_root == str(tmp_path.resolve())


def test_resolve_absolute_local_model_ref_within_models_root(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("train_core.config.settings.train_models_root", str(tmp_path))
    absolute_path = tmp_path / "llms/chat/qwen2.5-0.5b-instruct-4bit"

    resolved = resolve_model_ref(str(absolute_path), source_kind="local-path")

    assert resolved.resolved_ref == "llms/chat/qwen2.5-0.5b-instruct-4bit"
    assert resolved.resolved_path == str(absolute_path.resolve())


def test_resolve_local_model_ref_rejects_path_escape(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("train_core.config.settings.train_models_root", str(tmp_path))

    with pytest.raises(ModelResolutionError, match="outside TRAIN_MODELS_ROOT"):
        resolve_model_ref("../outside-model", source_kind="local-path")
