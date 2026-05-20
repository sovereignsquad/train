from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from train_core.config import settings


class ModelResolutionError(ValueError):
    """Raised when a model reference cannot be resolved safely."""


@dataclass(frozen=True)
class ResolvedModelRef:
    source_kind: str
    original_ref: str
    resolved_ref: str
    resolved_path: str | None
    models_root: str | None


def get_models_root() -> Path:
    return Path(settings.train_models_root).resolve()


def resolve_model_ref(model_ref: str, *, source_kind: str) -> ResolvedModelRef:
    normalized_ref = model_ref.strip()
    if not normalized_ref:
        raise ModelResolutionError("model_ref must not be empty")

    if source_kind in {"huggingface", "ollama"}:
        return ResolvedModelRef(
            source_kind=source_kind,
            original_ref=normalized_ref,
            resolved_ref=normalized_ref,
            resolved_path=None,
            models_root=None,
        )

    if source_kind != "local-path":
        raise ModelResolutionError(f"Unsupported model source kind '{source_kind}'")

    models_root = get_models_root()
    candidate = Path(normalized_ref)
    if candidate.is_absolute():
        resolved_path = candidate.resolve()
    else:
        resolved_path = (models_root / candidate).resolve()

    try:
        relative_ref = resolved_path.relative_to(models_root)
    except ValueError as exc:
        raise ModelResolutionError(
            f"Local model ref '{normalized_ref}' resolves outside TRAIN_MODELS_ROOT '{models_root}'."
        ) from exc

    return ResolvedModelRef(
        source_kind=source_kind,
        original_ref=normalized_ref,
        resolved_ref=str(relative_ref),
        resolved_path=str(resolved_path),
        models_root=str(models_root),
    )
