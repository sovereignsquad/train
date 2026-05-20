from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import re

from sqlalchemy.orm import Session

from train_core.db import SessionLocal
from train_core.fine_tuning import (
    FineTuningContractError,
    get_adapter_artifact,
    get_training_spec,
    serialize_adapter_artifact,
    update_adapter_artifact_packaging_metadata,
)
from train_core.schemas import AdapterArtifactRead


class OllamaPackagingError(ValueError):
    """Raised when an adapter artifact cannot be packaged for local Ollama use."""


@dataclass(frozen=True)
class OllamaPackageResult:
    adapter_artifact: AdapterArtifactRead
    ollama_model_name: str
    modelfile_path: str
    metadata_path: str
    output_dir: str
    created_at: str


def package_adapter_artifact_for_ollama(
    *,
    artifact_key: str,
    artifact_version: str,
    ollama_model_name: str,
    output_dir: str | Path | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    system_prompt: str | None = None,
    db: Session | None = None,
) -> OllamaPackageResult:
    if db is None:
        with SessionLocal() as owned_session:
            return _package_adapter_artifact_for_ollama(
                db=owned_session,
                artifact_key=artifact_key,
                artifact_version=artifact_version,
                ollama_model_name=ollama_model_name,
                output_dir=output_dir,
                temperature=temperature,
                top_p=top_p,
                system_prompt=system_prompt,
            )
    return _package_adapter_artifact_for_ollama(
        db=db,
        artifact_key=artifact_key,
        artifact_version=artifact_version,
        ollama_model_name=ollama_model_name,
        output_dir=output_dir,
        temperature=temperature,
        top_p=top_p,
        system_prompt=system_prompt,
    )


def _package_adapter_artifact_for_ollama(
    *,
    db: Session,
    artifact_key: str,
    artifact_version: str,
    ollama_model_name: str,
    output_dir: str | Path | None,
    temperature: float | None,
    top_p: float | None,
    system_prompt: str | None,
) -> OllamaPackageResult:
    artifact = get_adapter_artifact(artifact_key, artifact_version, db)
    if artifact is None:
        raise OllamaPackagingError(
            f"Adapter artifact '{artifact_key}' version '{artifact_version}' was not found."
        )
    spec = get_training_spec(artifact.training_spec_key, artifact.training_spec_version, db)
    if spec is None:
        raise OllamaPackagingError(
            f"Training spec '{artifact.training_spec_key}' version '{artifact.training_spec_version}' was not found."
        )
    if artifact.adapter_format != "safetensors":
        raise OllamaPackagingError("Only safetensors adapter artifacts are currently packageable for Ollama.")

    artifact_path = Path(artifact.artifact_path)
    if not artifact_path.exists():
        raise OllamaPackagingError(f"Adapter artifact path '{artifact_path}' does not exist.")

    resolved_output_dir = (
        Path(output_dir).expanduser().resolve()
        if output_dir is not None
        else _default_package_dir(artifact_path=artifact_path, ollama_model_name=ollama_model_name)
    )
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    modelfile_path = resolved_output_dir / "Modelfile"
    metadata_path = resolved_output_dir / "ollama-package.json"
    packaging_metadata = {
        "packaged_at": datetime.now(UTC).isoformat(),
        "ollama_model_name": ollama_model_name,
        "adapter_artifact_ref": artifact.ref,
        "training_spec_ref": spec.ref,
        "base_model_ref": artifact.base_model_ref,
        "base_model_source_kind": artifact.base_model_source_kind,
        "adapter_path": str(artifact_path.resolve()),
        "template_ref": artifact.template_ref,
        "tokenizer_ref": artifact.tokenizer_ref,
        "training_backend": artifact.training_backend,
        "training_method": artifact.training_method,
        "parameters": {
            "temperature": temperature,
            "top_p": top_p,
        },
        "system_prompt": system_prompt,
    }
    metadata_path.write_text(json.dumps(packaging_metadata, indent=2, sort_keys=True), encoding="utf-8")
    modelfile_path.write_text(
        _render_modelfile(
            base_model_ref=artifact.base_model_ref,
            adapter_path=artifact_path,
            temperature=temperature,
            top_p=top_p,
            system_prompt=system_prompt,
        ),
        encoding="utf-8",
    )

    try:
        updated_artifact = update_adapter_artifact_packaging_metadata(
            db,
            artifact.key,
            artifact.version,
            packaging_metadata_path=str(metadata_path.resolve()),
        )
    except FineTuningContractError as exc:
        raise OllamaPackagingError(str(exc)) from exc

    return OllamaPackageResult(
        adapter_artifact=serialize_adapter_artifact(updated_artifact),
        ollama_model_name=ollama_model_name,
        modelfile_path=str(modelfile_path.resolve()),
        metadata_path=str(metadata_path.resolve()),
        output_dir=str(resolved_output_dir.resolve()),
        created_at=packaging_metadata["packaged_at"],
    )


def _default_package_dir(*, artifact_path: Path, ollama_model_name: str) -> Path:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", ollama_model_name.strip()).strip("-") or "ollama-adapter"
    anchor = artifact_path if artifact_path.is_dir() else artifact_path.parent
    return (anchor / "ollama-package" / slug).resolve()


def _render_modelfile(
    *,
    base_model_ref: str,
    adapter_path: Path,
    temperature: float | None,
    top_p: float | None,
    system_prompt: str | None,
) -> str:
    lines = [
        f"FROM {base_model_ref}",
        f"ADAPTER {adapter_path.resolve()}",
    ]
    if temperature is not None:
        lines.append(f"PARAMETER temperature {temperature}")
    if top_p is not None:
        lines.append(f"PARAMETER top_p {top_p}")
    if system_prompt:
        escaped = system_prompt.replace('"', '\\"')
        lines.append(f'SYSTEM "{escaped}"')
    lines.append("")
    return "\n".join(lines)
