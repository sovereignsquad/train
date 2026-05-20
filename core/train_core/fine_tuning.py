from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from train_core.datasets import EvalDatasetError, get_eval_dataset, get_eval_dataset_slice
from train_core.db import SessionLocal
from train_core.grader_suites import GraderSuiteError, get_grader_suite
from train_core.models import AdapterArtifactRecord, TrainingSpecRecord
from train_core.schemas import (
    AdapterArtifactRead,
    AdapterArtifactWrite,
    TrainingSpecRead,
    TrainingSpecWrite,
)


class FineTuningContractError(ValueError):
    """Raised when a fine-tuning contract operation is invalid."""


@dataclass(frozen=True)
class TrainingSpecDefinition:
    key: str
    version: str
    ref: str
    name: str
    description: str
    dataset_key: str
    dataset_version: str
    dataset_ref: str
    dataset_slice_key: str | None
    dataset_slice_version: str | None
    dataset_slice_ref: str | None
    grader_suite_key: str
    grader_suite_version: str
    grader_suite_ref: str
    base_model_ref: str
    base_model_source_kind: str
    template_ref: str
    tokenizer_ref: str | None
    training_backend: str
    training_stage: str
    training_method: str
    expected_adapter_family: str
    output_dir: str
    hyperparameters: dict[str, object]
    provenance: dict[str, object]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class AdapterArtifactDefinition:
    key: str
    version: str
    ref: str
    training_spec_key: str
    training_spec_version: str
    training_spec_ref: str
    name: str
    description: str
    dataset_key: str
    dataset_version: str
    dataset_ref: str
    dataset_slice_key: str | None
    dataset_slice_version: str | None
    dataset_slice_ref: str | None
    grader_suite_key: str
    grader_suite_version: str
    grader_suite_ref: str
    base_model_ref: str
    base_model_source_kind: str
    template_ref: str
    tokenizer_ref: str | None
    training_backend: str
    training_stage: str
    training_method: str
    adapter_family: str
    adapter_format: str
    artifact_path: str
    checkpoint_path: str | None
    training_log_path: str | None
    packaging_metadata_path: str | None
    provenance: dict[str, object]
    created_at: datetime
    updated_at: datetime


def list_training_specs(db: Session | None = None) -> list[TrainingSpecDefinition]:
    if db is None:
        with SessionLocal() as owned_session:
            return _list_training_specs(owned_session)
    return _list_training_specs(db)


def get_training_spec(key: str, version: str, db: Session | None = None) -> TrainingSpecDefinition | None:
    if db is None:
        with SessionLocal() as owned_session:
            return _get_training_spec(owned_session, key, version)
    return _get_training_spec(db, key, version)


def create_training_spec(db: Session, payload: TrainingSpecWrite) -> TrainingSpecDefinition:
    _require_fine_tuning_tables(db)
    if _get_training_spec(db, payload.key, payload.version) is not None:
        raise FineTuningContractError(
            f"Training spec '{payload.key}' version '{payload.version}' already exists."
        )
    _require_dataset_and_suite(db, payload)
    row = TrainingSpecRecord(
        key=payload.key,
        version=payload.version,
        name=payload.name,
        description=payload.description,
        dataset_key=payload.dataset_key,
        dataset_version=payload.dataset_version,
        dataset_slice_key=payload.dataset_slice_key,
        dataset_slice_version=payload.dataset_slice_version,
        grader_suite_key=payload.grader_suite_key,
        grader_suite_version=payload.grader_suite_version,
        base_model_ref=payload.base_model_ref,
        base_model_source_kind=payload.base_model_source_kind,
        template_ref=payload.template_ref,
        tokenizer_ref=payload.tokenizer_ref,
        training_backend=payload.training_backend,
        training_stage=payload.training_stage,
        training_method=payload.training_method,
        expected_adapter_family=payload.expected_adapter_family,
        output_dir=payload.output_dir,
        hyperparameters_json=json.dumps(payload.hyperparameters, sort_keys=True),
        provenance_json=json.dumps(payload.provenance, sort_keys=True),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _training_spec_row_to_definition(row)


def delete_training_spec(db: Session, key: str, version: str) -> None:
    _require_fine_tuning_tables(db)
    row = (
        db.query(TrainingSpecRecord)
        .filter(TrainingSpecRecord.key == key, TrainingSpecRecord.version == version)
        .one_or_none()
    )
    if row is None:
        raise FineTuningContractError(f"Training spec '{key}' version '{version}' was not found.")
    db.query(AdapterArtifactRecord).filter(
        AdapterArtifactRecord.training_spec_key == key,
        AdapterArtifactRecord.training_spec_version == version,
    ).delete()
    db.delete(row)
    db.commit()


def list_adapter_artifacts(db: Session | None = None) -> list[AdapterArtifactDefinition]:
    if db is None:
        with SessionLocal() as owned_session:
            return _list_adapter_artifacts(owned_session)
    return _list_adapter_artifacts(db)


def get_adapter_artifact(key: str, version: str, db: Session | None = None) -> AdapterArtifactDefinition | None:
    if db is None:
        with SessionLocal() as owned_session:
            return _get_adapter_artifact(owned_session, key, version)
    return _get_adapter_artifact(db, key, version)


def create_adapter_artifact(db: Session, payload: AdapterArtifactWrite) -> AdapterArtifactDefinition:
    _require_fine_tuning_tables(db)
    if _get_adapter_artifact(db, payload.key, payload.version) is not None:
        raise FineTuningContractError(
            f"Adapter artifact '{payload.key}' version '{payload.version}' already exists."
        )
    training_spec = _get_training_spec(db, payload.training_spec_key, payload.training_spec_version)
    if training_spec is None:
        raise FineTuningContractError(
            f"Training spec '{payload.training_spec_key}' version "
            f"'{payload.training_spec_version}' was not found."
        )
    row = AdapterArtifactRecord(
        key=payload.key,
        version=payload.version,
        training_spec_key=training_spec.key,
        training_spec_version=training_spec.version,
        name=payload.name,
        description=payload.description,
        dataset_key=training_spec.dataset_key,
        dataset_version=training_spec.dataset_version,
        dataset_slice_key=training_spec.dataset_slice_key,
        dataset_slice_version=training_spec.dataset_slice_version,
        grader_suite_key=training_spec.grader_suite_key,
        grader_suite_version=training_spec.grader_suite_version,
        base_model_ref=training_spec.base_model_ref,
        base_model_source_kind=training_spec.base_model_source_kind,
        template_ref=training_spec.template_ref,
        tokenizer_ref=training_spec.tokenizer_ref,
        training_backend=training_spec.training_backend,
        training_stage=training_spec.training_stage,
        training_method=training_spec.training_method,
        adapter_family=training_spec.expected_adapter_family,
        adapter_format=payload.adapter_format,
        artifact_path=payload.artifact_path,
        checkpoint_path=payload.checkpoint_path,
        training_log_path=payload.training_log_path,
        packaging_metadata_path=payload.packaging_metadata_path,
        provenance_json=json.dumps(payload.provenance, sort_keys=True),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _adapter_artifact_row_to_definition(row)


def delete_adapter_artifact(db: Session, key: str, version: str) -> None:
    _require_fine_tuning_tables(db)
    row = (
        db.query(AdapterArtifactRecord)
        .filter(AdapterArtifactRecord.key == key, AdapterArtifactRecord.version == version)
        .one_or_none()
    )
    if row is None:
        raise FineTuningContractError(f"Adapter artifact '{key}' version '{version}' was not found.")
    db.delete(row)
    db.commit()


def update_adapter_artifact_packaging_metadata(
    db: Session,
    key: str,
    version: str,
    *,
    packaging_metadata_path: str,
) -> AdapterArtifactDefinition:
    _require_fine_tuning_tables(db)
    row = (
        db.query(AdapterArtifactRecord)
        .filter(AdapterArtifactRecord.key == key, AdapterArtifactRecord.version == version)
        .one_or_none()
    )
    if row is None:
        raise FineTuningContractError(f"Adapter artifact '{key}' version '{version}' was not found.")
    row.packaging_metadata_path = packaging_metadata_path
    db.add(row)
    db.commit()
    db.refresh(row)
    return _adapter_artifact_row_to_definition(row)


def serialize_training_spec(definition: TrainingSpecDefinition) -> TrainingSpecRead:
    return TrainingSpecRead(**definition.__dict__)


def serialize_adapter_artifact(definition: AdapterArtifactDefinition) -> AdapterArtifactRead:
    return AdapterArtifactRead(**definition.__dict__)


def _list_training_specs(db: Session) -> list[TrainingSpecDefinition]:
    if not _fine_tuning_tables_exist(db):
        return []
    rows = (
        db.query(TrainingSpecRecord)
        .order_by(TrainingSpecRecord.key.asc(), TrainingSpecRecord.version.asc())
        .all()
    )
    return [_training_spec_row_to_definition(row) for row in rows]


def _get_training_spec(db: Session, key: str, version: str) -> TrainingSpecDefinition | None:
    if not _fine_tuning_tables_exist(db):
        return None
    row = (
        db.query(TrainingSpecRecord)
        .filter(TrainingSpecRecord.key == key, TrainingSpecRecord.version == version)
        .one_or_none()
    )
    return None if row is None else _training_spec_row_to_definition(row)


def _list_adapter_artifacts(db: Session) -> list[AdapterArtifactDefinition]:
    if not _fine_tuning_tables_exist(db):
        return []
    rows = (
        db.query(AdapterArtifactRecord)
        .order_by(AdapterArtifactRecord.key.asc(), AdapterArtifactRecord.version.asc())
        .all()
    )
    return [_adapter_artifact_row_to_definition(row) for row in rows]


def _get_adapter_artifact(db: Session, key: str, version: str) -> AdapterArtifactDefinition | None:
    if not _fine_tuning_tables_exist(db):
        return None
    row = (
        db.query(AdapterArtifactRecord)
        .filter(AdapterArtifactRecord.key == key, AdapterArtifactRecord.version == version)
        .one_or_none()
    )
    return None if row is None else _adapter_artifact_row_to_definition(row)


def _require_dataset_and_suite(db: Session, payload: TrainingSpecWrite) -> None:
    dataset = get_eval_dataset(payload.dataset_key, payload.dataset_version, db)
    if dataset is None:
        raise EvalDatasetError(
            f"Eval dataset '{payload.dataset_key}' version '{payload.dataset_version}' was not found."
        )
    if payload.dataset_slice_key is not None:
        dataset_slice = get_eval_dataset_slice(
            payload.dataset_key,
            payload.dataset_version,
            payload.dataset_slice_key,
            payload.dataset_slice_version or "",
            db,
        )
        if dataset_slice is None:
            raise EvalDatasetError(
                f"Eval dataset slice '{payload.dataset_slice_key}' version "
                f"'{payload.dataset_slice_version}' was not found for dataset "
                f"'{payload.dataset_key}' version '{payload.dataset_version}'."
            )
    suite = get_grader_suite(
        payload.dataset_key,
        payload.dataset_version,
        payload.grader_suite_key,
        payload.grader_suite_version,
        db,
    )
    if suite is None:
        raise GraderSuiteError(
            f"Grader suite '{payload.grader_suite_key}' version '{payload.grader_suite_version}' "
            f"was not found for dataset '{payload.dataset_key}' version '{payload.dataset_version}'."
        )


def _training_spec_row_to_definition(row: TrainingSpecRecord) -> TrainingSpecDefinition:
    dataset_ref = f"{row.dataset_key}@{row.dataset_version}"
    dataset_slice_ref = None
    if row.dataset_slice_key and row.dataset_slice_version:
        dataset_slice_ref = (
            f"{row.dataset_key}@{row.dataset_version}:"
            f"{row.dataset_slice_key}@{row.dataset_slice_version}"
        )
    grader_suite_ref = (
        f"{row.dataset_key}@{row.dataset_version}:"
        f"{row.grader_suite_key}@{row.grader_suite_version}"
    )
    return TrainingSpecDefinition(
        key=row.key,
        version=row.version,
        ref=f"{row.key}@{row.version}",
        name=row.name,
        description=row.description,
        dataset_key=row.dataset_key,
        dataset_version=row.dataset_version,
        dataset_ref=dataset_ref,
        dataset_slice_key=row.dataset_slice_key,
        dataset_slice_version=row.dataset_slice_version,
        dataset_slice_ref=dataset_slice_ref,
        grader_suite_key=row.grader_suite_key,
        grader_suite_version=row.grader_suite_version,
        grader_suite_ref=grader_suite_ref,
        base_model_ref=row.base_model_ref,
        base_model_source_kind=row.base_model_source_kind,
        template_ref=row.template_ref,
        tokenizer_ref=row.tokenizer_ref,
        training_backend=row.training_backend,
        training_stage=row.training_stage,
        training_method=row.training_method,
        expected_adapter_family=row.expected_adapter_family,
        output_dir=row.output_dir,
        hyperparameters=json.loads(row.hyperparameters_json),
        provenance=json.loads(row.provenance_json),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _adapter_artifact_row_to_definition(row: AdapterArtifactRecord) -> AdapterArtifactDefinition:
    dataset_ref = f"{row.dataset_key}@{row.dataset_version}"
    dataset_slice_ref = None
    if row.dataset_slice_key and row.dataset_slice_version:
        dataset_slice_ref = (
            f"{row.dataset_key}@{row.dataset_version}:"
            f"{row.dataset_slice_key}@{row.dataset_slice_version}"
        )
    grader_suite_ref = (
        f"{row.dataset_key}@{row.dataset_version}:"
        f"{row.grader_suite_key}@{row.grader_suite_version}"
    )
    training_spec_ref = f"{row.training_spec_key}@{row.training_spec_version}"
    return AdapterArtifactDefinition(
        key=row.key,
        version=row.version,
        ref=f"{row.key}@{row.version}",
        training_spec_key=row.training_spec_key,
        training_spec_version=row.training_spec_version,
        training_spec_ref=training_spec_ref,
        name=row.name,
        description=row.description,
        dataset_key=row.dataset_key,
        dataset_version=row.dataset_version,
        dataset_ref=dataset_ref,
        dataset_slice_key=row.dataset_slice_key,
        dataset_slice_version=row.dataset_slice_version,
        dataset_slice_ref=dataset_slice_ref,
        grader_suite_key=row.grader_suite_key,
        grader_suite_version=row.grader_suite_version,
        grader_suite_ref=grader_suite_ref,
        base_model_ref=row.base_model_ref,
        base_model_source_kind=row.base_model_source_kind,
        template_ref=row.template_ref,
        tokenizer_ref=row.tokenizer_ref,
        training_backend=row.training_backend,
        training_stage=row.training_stage,
        training_method=row.training_method,
        adapter_family=row.adapter_family,
        adapter_format=row.adapter_format,
        artifact_path=row.artifact_path,
        checkpoint_path=row.checkpoint_path,
        training_log_path=row.training_log_path,
        packaging_metadata_path=row.packaging_metadata_path,
        provenance=json.loads(row.provenance_json),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _fine_tuning_tables_exist(db: Session) -> bool:
    inspector = inspect(db.bind)
    table_names = set(inspector.get_table_names())
    return {"training_specs", "adapter_artifacts"}.issubset(table_names)


def _require_fine_tuning_tables(db: Session) -> None:
    if _fine_tuning_tables_exist(db):
        return
    raise FineTuningContractError(
        "Offline fine-tuning contract tables are not available. Run database migrations first."
    )
