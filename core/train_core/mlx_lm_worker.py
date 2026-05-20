from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import subprocess
import sys

from sqlalchemy.orm import Session

from train_core.datasets import get_eval_dataset, get_eval_dataset_slice
from train_core.db import SessionLocal
from train_core.fine_tuning import (
    create_adapter_artifact,
    get_training_spec,
    serialize_adapter_artifact,
)
from train_core.health import TrainingReadinessError, assert_training_lane_ready
from train_core.model_resolution import resolve_model_ref
from train_core.schemas import AdapterArtifactWrite, TrainingSpecRunRead, TrainingSpecRunRequest


class MlxLmWorkerError(ValueError):
    """Raised when the mlx-lm worker cannot complete a training run."""


@dataclass(frozen=True)
class PartitionedDatasetFiles:
    train: tuple[Path, ...]
    valid: tuple[Path, ...]
    test: tuple[Path, ...]


def run_training_spec_with_mlx_lm(
    spec_key: str,
    spec_version: str,
    payload: TrainingSpecRunRequest,
    db: Session | None = None,
) -> TrainingSpecRunRead:
    if db is None:
        with SessionLocal() as owned_session:
            return _run_training_spec_with_mlx_lm(owned_session, spec_key, spec_version, payload)
    return _run_training_spec_with_mlx_lm(db, spec_key, spec_version, payload)


def _run_training_spec_with_mlx_lm(
    db: Session,
    spec_key: str,
    spec_version: str,
    payload: TrainingSpecRunRequest,
) -> TrainingSpecRunRead:
    spec = get_training_spec(spec_key, spec_version, db)
    if spec is None:
        raise MlxLmWorkerError(f"Training spec '{spec_key}' version '{spec_version}' was not found.")
    if spec.training_backend != "mlx-lm":
        raise MlxLmWorkerError("Training spec backend is not mlx-lm.")
    try:
        assert_training_lane_ready(spec=spec)
    except TrainingReadinessError as exc:
        raise MlxLmWorkerError(str(exc)) from exc

    run_root = Path(spec.output_dir) / spec.key / spec.version / payload.adapter_key / payload.adapter_version
    data_dir = run_root / "data"
    adapter_dir = run_root / "adapters"
    metadata_path = run_root / "training-result.json"
    training_log_path = run_root / "train.log"
    data_dir.mkdir(parents=True, exist_ok=True)
    adapter_dir.mkdir(parents=True, exist_ok=True)

    _export_dataset_for_mlx_lm(db, spec_key, spec_version, data_dir)
    command = _build_mlx_lm_command(spec, data_dir=data_dir, adapter_dir=adapter_dir)
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    log_content = ""
    if completed.stdout:
        log_content += completed.stdout
    if completed.stderr:
        if log_content:
            log_content += "\n"
        log_content += completed.stderr
    training_log_path.write_text(log_content, encoding="utf-8")
    if completed.returncode != 0:
        raise MlxLmWorkerError(
            f"mlx-lm training failed for {spec.ref} with exit code {completed.returncode}. "
            f"See {training_log_path} for details."
        )

    adapter_file = adapter_dir / "adapters.safetensors"
    artifact_path = adapter_file if adapter_file.exists() else adapter_dir
    resolved_model = resolve_model_ref(spec.base_model_ref, source_kind=spec.base_model_source_kind)
    metadata_payload = {
        "training_spec_ref": spec.ref,
        "training_backend": spec.training_backend,
        "training_method": spec.training_method,
        "base_model_ref": spec.base_model_ref,
        "base_model_source_kind": spec.base_model_source_kind,
        "resolved_base_model_ref": resolved_model.resolved_ref,
        "resolved_base_model_path": resolved_model.resolved_path,
        "data_dir": str(data_dir),
        "adapter_dir": str(adapter_dir),
        "artifact_path": str(artifact_path),
        "training_log_path": str(training_log_path),
        "command": command,
        "completed_at": datetime.now(UTC).isoformat(),
    }
    metadata_path.write_text(json.dumps(metadata_payload, indent=2, sort_keys=True), encoding="utf-8")

    artifact = create_adapter_artifact(
        db,
        AdapterArtifactWrite(
            key=payload.adapter_key,
            version=payload.adapter_version,
            training_spec_key=spec.key,
            training_spec_version=spec.version,
            name=payload.adapter_name,
            description=payload.adapter_description,
            adapter_format=payload.artifact_format,
            artifact_path=str(artifact_path.resolve()),
            training_log_path=str(training_log_path.resolve()),
            provenance={
                **payload.provenance,
                "worker": "mlx-lm",
                "metadata_path": str(metadata_path.resolve()),
                "data_dir": str(data_dir.resolve()),
            },
        ),
    )
    return TrainingSpecRunRead(
        training_spec_ref=spec.ref,
        training_backend=spec.training_backend,
        training_method=spec.training_method,
        data_dir=str(data_dir.resolve()),
        adapter_dir=str(adapter_dir.resolve()),
        training_log_path=str(training_log_path.resolve()),
        metadata_path=str(metadata_path.resolve()),
        command=tuple(command),
        adapter_artifact=serialize_adapter_artifact(artifact),
    )


def _export_dataset_for_mlx_lm(db: Session, spec_key: str, spec_version: str, output_dir: Path) -> None:
    spec = get_training_spec(spec_key, spec_version, db)
    if spec is None:
        raise MlxLmWorkerError(f"Training spec '{spec_key}' version '{spec_version}' was not found.")
    dataset = get_eval_dataset(spec.dataset_key, spec.dataset_version, db)
    if dataset is None:
        raise MlxLmWorkerError(
            f"Eval dataset '{spec.dataset_key}' version '{spec.dataset_version}' was not found."
        )
    selected_item_keys: set[str] | None = None
    if spec.dataset_slice_key and spec.dataset_slice_version:
        dataset_slice = get_eval_dataset_slice(
            spec.dataset_key,
            spec.dataset_version,
            spec.dataset_slice_key,
            spec.dataset_slice_version,
            db,
        )
        if dataset_slice is None:
            raise MlxLmWorkerError(
                f"Eval dataset slice '{spec.dataset_slice_key}' version '{spec.dataset_slice_version}' "
                f"was not found for dataset '{spec.dataset_key}' version '{spec.dataset_version}'."
            )
        selected_item_keys = set(dataset_slice.selection_item_keys)
    files = _partition_dataset_files(dataset.items, selected_item_keys=selected_item_keys)
    _write_partition(output_dir / "train.jsonl", files.train)
    if files.valid:
        _write_partition(output_dir / "valid.jsonl", files.valid)
    if files.test:
        _write_partition(output_dir / "test.jsonl", files.test)


def _partition_dataset_files(items, *, selected_item_keys: set[str] | None) -> PartitionedDatasetFiles:
    train: list[Path] = []
    valid: list[Path] = []
    test: list[Path] = []
    for item in items:
        if selected_item_keys is not None and item.item_key not in selected_item_keys:
            continue
        path = Path(item.path)
        if path.suffix != ".jsonl":
            raise MlxLmWorkerError("mlx-lm worker requires dataset items to be .jsonl files")
        partition = str(item.labels.get("partition") or "train").strip().lower()
        if partition == "train":
            train.append(path)
        elif partition in {"valid", "validation"}:
            valid.append(path)
        elif partition == "test":
            test.append(path)
        else:
            raise MlxLmWorkerError(
                f"Unsupported dataset partition label '{partition}' for item '{item.item_key}'."
            )
    if not train:
        raise MlxLmWorkerError("mlx-lm worker requires at least one train partition dataset item")
    return PartitionedDatasetFiles(train=tuple(train), valid=tuple(valid), test=tuple(test))


def _write_partition(destination: Path, sources: tuple[Path, ...]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for index, source in enumerate(sources):
            content = source.read_text(encoding="utf-8")
            if content and not content.endswith("\n"):
                content += "\n"
            handle.write(content)
            if index == len(sources) - 1:
                continue


def _build_mlx_lm_command(spec, *, data_dir: Path, adapter_dir: Path) -> list[str]:
    resolved_model = resolve_model_ref(spec.base_model_ref, source_kind=spec.base_model_source_kind)
    command = [
        sys.executable,
        "-m",
        "mlx_lm.lora",
        "--model",
        resolved_model.resolved_path or resolved_model.resolved_ref,
        "--train",
        "--data",
        str(data_dir.resolve()),
        "--adapter-path",
        str(adapter_dir.resolve()),
    ]
    reserved = {"model", "data", "adapter_path", "adapter-path", "train", "test"}
    for key, value in sorted(spec.hyperparameters.items()):
        normalized = str(key).strip()
        if normalized in reserved:
            raise MlxLmWorkerError(f"Hyperparameter '{key}' is reserved by the mlx-lm worker")
        flag = f"--{normalized.replace('_', '-')}"
        if isinstance(value, bool):
            if value:
                command.append(flag)
            continue
        if isinstance(value, (str, int, float)):
            command.extend([flag, str(value)])
            continue
        if isinstance(value, (list, tuple)):
            for item in value:
                command.extend([flag, str(item)])
            continue
        raise MlxLmWorkerError(
            f"Hyperparameter '{key}' has unsupported value type '{type(value).__name__}'."
        )
    return command
