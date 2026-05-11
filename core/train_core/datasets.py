from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from train_core.db import SessionLocal
from train_core.models import EvalDatasetRecord, EvalDatasetSliceRecord, GraderSuiteRecord
from train_core.schemas import (
    EvalDatasetItem,
    EvalDatasetRead,
    EvalDatasetSliceRead,
    EvalDatasetSliceWrite,
    EvalDatasetWrite,
)


class EvalDatasetError(ValueError):
    """Raised when an eval dataset operation is invalid."""


@dataclass(frozen=True)
class EvalDatasetDefinition:
    key: str
    version: str
    ref: str
    name: str
    description: str
    source_kind: str
    scope_kind: str
    scope_value: str | None
    items: tuple[EvalDatasetItem, ...]
    provenance: dict[str, object]
    item_count: int
    fingerprint: str


@dataclass(frozen=True)
class EvalDatasetSliceDefinition:
    dataset_key: str
    dataset_version: str
    dataset_ref: str
    key: str
    version: str
    ref: str
    name: str
    description: str
    scope_kind: str
    scope_value: str | None
    selection_item_keys: tuple[str, ...]
    provenance: dict[str, object]
    item_count: int
    fingerprint: str


def list_eval_datasets(db: Session | None = None) -> list[EvalDatasetDefinition]:
    if db is None:
        with SessionLocal() as owned_session:
            return _list_eval_datasets(owned_session)
    return _list_eval_datasets(db)


def get_eval_dataset(key: str, version: str, db: Session | None = None) -> EvalDatasetDefinition | None:
    if db is None:
        with SessionLocal() as owned_session:
            return _get_eval_dataset(owned_session, key, version)
    return _get_eval_dataset(db, key, version)


def create_eval_dataset(db: Session, payload: EvalDatasetWrite) -> EvalDatasetDefinition:
    _require_eval_dataset_tables(db)
    if _get_eval_dataset(db, payload.key, payload.version) is not None:
        raise EvalDatasetError(
            f"Eval dataset '{payload.key}' version '{payload.version}' already exists."
        )
    item_count = len(payload.items)
    fingerprint = _fingerprint_dataset_items(payload.items)
    row = EvalDatasetRecord(
        key=payload.key,
        version=payload.version,
        name=payload.name,
        description=payload.description,
        source_kind=payload.source_kind,
        scope_kind=payload.scope_kind,
        scope_value=payload.scope_value,
        items_json=json.dumps([item.model_dump(mode="json") for item in payload.items], sort_keys=True),
        provenance_json=json.dumps(payload.provenance, sort_keys=True),
        item_count=item_count,
        fingerprint=fingerprint,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _dataset_row_to_definition(row)


def delete_eval_dataset(db: Session, key: str, version: str) -> None:
    _require_eval_dataset_tables(db)
    row = (
        db.query(EvalDatasetRecord)
        .filter(EvalDatasetRecord.key == key, EvalDatasetRecord.version == version)
        .one_or_none()
    )
    if row is None:
        raise EvalDatasetError(f"Eval dataset '{key}' version '{version}' was not found.")
    db.query(EvalDatasetSliceRecord).filter(
        EvalDatasetSliceRecord.dataset_key == key,
        EvalDatasetSliceRecord.dataset_version == version,
    ).delete()
    db.query(GraderSuiteRecord).filter(
        GraderSuiteRecord.dataset_key == key,
        GraderSuiteRecord.dataset_version == version,
    ).delete()
    db.delete(row)
    db.commit()


def list_eval_dataset_slices(
    dataset_key: str,
    dataset_version: str,
    db: Session | None = None,
) -> list[EvalDatasetSliceDefinition]:
    if db is None:
        with SessionLocal() as owned_session:
            return _list_eval_dataset_slices(owned_session, dataset_key, dataset_version)
    return _list_eval_dataset_slices(db, dataset_key, dataset_version)


def get_eval_dataset_slice(
    dataset_key: str,
    dataset_version: str,
    key: str,
    version: str,
    db: Session | None = None,
) -> EvalDatasetSliceDefinition | None:
    if db is None:
        with SessionLocal() as owned_session:
            return _get_eval_dataset_slice(owned_session, dataset_key, dataset_version, key, version)
    return _get_eval_dataset_slice(db, dataset_key, dataset_version, key, version)


def create_eval_dataset_slice(
    db: Session,
    dataset_key: str,
    dataset_version: str,
    payload: EvalDatasetSliceWrite,
) -> EvalDatasetSliceDefinition:
    _require_eval_dataset_tables(db)
    dataset = _get_eval_dataset(db, dataset_key, dataset_version)
    if dataset is None:
        raise EvalDatasetError(
            f"Eval dataset '{dataset_key}' version '{dataset_version}' was not found."
        )
    if _get_eval_dataset_slice(db, dataset_key, dataset_version, payload.key, payload.version) is not None:
        raise EvalDatasetError(
            f"Eval dataset slice '{payload.key}' version '{payload.version}' already exists."
        )
    dataset_item_keys = {item.item_key for item in dataset.items}
    missing = sorted(set(payload.selection_item_keys) - dataset_item_keys)
    if missing:
        raise EvalDatasetError(
            f"Eval dataset slice references unknown item_key values: {', '.join(missing)}"
        )
    fingerprint = _fingerprint_slice_items(dataset, payload.selection_item_keys)
    row = EvalDatasetSliceRecord(
        dataset_key=dataset_key,
        dataset_version=dataset_version,
        key=payload.key,
        version=payload.version,
        name=payload.name,
        description=payload.description,
        scope_kind=payload.scope_kind,
        scope_value=payload.scope_value,
        selection_item_keys_json=json.dumps(list(payload.selection_item_keys), sort_keys=True),
        provenance_json=json.dumps(payload.provenance, sort_keys=True),
        item_count=len(payload.selection_item_keys),
        fingerprint=fingerprint,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _slice_row_to_definition(row)


def delete_eval_dataset_slice(
    db: Session,
    dataset_key: str,
    dataset_version: str,
    key: str,
    version: str,
) -> None:
    _require_eval_dataset_tables(db)
    row = (
        db.query(EvalDatasetSliceRecord)
        .filter(
            EvalDatasetSliceRecord.dataset_key == dataset_key,
            EvalDatasetSliceRecord.dataset_version == dataset_version,
            EvalDatasetSliceRecord.key == key,
            EvalDatasetSliceRecord.version == version,
        )
        .one_or_none()
    )
    if row is None:
        raise EvalDatasetError(
            f"Eval dataset slice '{key}' version '{version}' was not found for dataset "
            f"'{dataset_key}' version '{dataset_version}'."
        )
    db.delete(row)
    db.commit()


def resolve_eval_dataset_paths(
    *,
    dataset_key: str,
    dataset_version: str,
    slice_key: str | None = None,
    slice_version: str | None = None,
    db: Session | None = None,
) -> tuple[str, ...]:
    if db is None:
        with SessionLocal() as owned_session:
            return _resolve_eval_dataset_paths(
                owned_session,
                dataset_key=dataset_key,
                dataset_version=dataset_version,
                slice_key=slice_key,
                slice_version=slice_version,
            )
    return _resolve_eval_dataset_paths(
        db,
        dataset_key=dataset_key,
        dataset_version=dataset_version,
        slice_key=slice_key,
        slice_version=slice_version,
    )


def serialize_eval_dataset(definition: EvalDatasetDefinition) -> EvalDatasetRead:
    return EvalDatasetRead(**definition.__dict__)


def serialize_eval_dataset_slice(definition: EvalDatasetSliceDefinition) -> EvalDatasetSliceRead:
    return EvalDatasetSliceRead(**definition.__dict__)


def _list_eval_datasets(db: Session) -> list[EvalDatasetDefinition]:
    if not _eval_dataset_tables_exist(db):
        return []
    rows = (
        db.query(EvalDatasetRecord)
        .order_by(EvalDatasetRecord.key.asc(), EvalDatasetRecord.version.asc())
        .all()
    )
    return [_dataset_row_to_definition(row) for row in rows]


def _get_eval_dataset(db: Session, key: str, version: str) -> EvalDatasetDefinition | None:
    if not _eval_dataset_tables_exist(db):
        return None
    row = (
        db.query(EvalDatasetRecord)
        .filter(EvalDatasetRecord.key == key, EvalDatasetRecord.version == version)
        .one_or_none()
    )
    return None if row is None else _dataset_row_to_definition(row)


def _list_eval_dataset_slices(
    db: Session,
    dataset_key: str,
    dataset_version: str,
) -> list[EvalDatasetSliceDefinition]:
    if not _eval_dataset_tables_exist(db):
        return []
    rows = (
        db.query(EvalDatasetSliceRecord)
        .filter(
            EvalDatasetSliceRecord.dataset_key == dataset_key,
            EvalDatasetSliceRecord.dataset_version == dataset_version,
        )
        .order_by(EvalDatasetSliceRecord.key.asc(), EvalDatasetSliceRecord.version.asc())
        .all()
    )
    return [_slice_row_to_definition(row) for row in rows]


def _get_eval_dataset_slice(
    db: Session,
    dataset_key: str,
    dataset_version: str,
    key: str,
    version: str,
) -> EvalDatasetSliceDefinition | None:
    if not _eval_dataset_tables_exist(db):
        return None
    row = (
        db.query(EvalDatasetSliceRecord)
        .filter(
            EvalDatasetSliceRecord.dataset_key == dataset_key,
            EvalDatasetSliceRecord.dataset_version == dataset_version,
            EvalDatasetSliceRecord.key == key,
            EvalDatasetSliceRecord.version == version,
        )
        .one_or_none()
    )
    return None if row is None else _slice_row_to_definition(row)


def _resolve_eval_dataset_paths(
    db: Session,
    *,
    dataset_key: str,
    dataset_version: str,
    slice_key: str | None,
    slice_version: str | None,
) -> tuple[str, ...]:
    dataset = _get_eval_dataset(db, dataset_key, dataset_version)
    if dataset is None:
        raise EvalDatasetError(
            f"Eval dataset '{dataset_key}' version '{dataset_version}' was not found."
        )
    item_map = {item.item_key: item.path for item in dataset.items}
    if slice_key is None and slice_version is None:
        return tuple(item.path for item in dataset.items)
    if not slice_key or not slice_version:
        raise EvalDatasetError("slice_key and slice_version must be provided together")
    slice_definition = _get_eval_dataset_slice(db, dataset_key, dataset_version, slice_key, slice_version)
    if slice_definition is None:
        raise EvalDatasetError(
            f"Eval dataset slice '{slice_key}' version '{slice_version}' was not found for dataset "
            f"'{dataset_key}' version '{dataset_version}'."
        )
    return tuple(item_map[item_key] for item_key in slice_definition.selection_item_keys)


def _dataset_row_to_definition(row: EvalDatasetRecord) -> EvalDatasetDefinition:
    items = tuple(EvalDatasetItem.model_validate(item) for item in json.loads(row.items_json))
    provenance = dict(json.loads(row.provenance_json))
    return EvalDatasetDefinition(
        key=row.key,
        version=row.version,
        ref=f"{row.key}@{row.version}",
        name=row.name,
        description=row.description,
        source_kind=row.source_kind,
        scope_kind=row.scope_kind,
        scope_value=row.scope_value,
        items=items,
        provenance=provenance,
        item_count=row.item_count,
        fingerprint=row.fingerprint,
    )


def _slice_row_to_definition(row: EvalDatasetSliceRecord) -> EvalDatasetSliceDefinition:
    selection_item_keys = tuple(str(item) for item in json.loads(row.selection_item_keys_json))
    provenance = dict(json.loads(row.provenance_json))
    dataset_ref = f"{row.dataset_key}@{row.dataset_version}"
    return EvalDatasetSliceDefinition(
        dataset_key=row.dataset_key,
        dataset_version=row.dataset_version,
        dataset_ref=dataset_ref,
        key=row.key,
        version=row.version,
        ref=f"{dataset_ref}:{row.key}@{row.version}",
        name=row.name,
        description=row.description,
        scope_kind=row.scope_kind,
        scope_value=row.scope_value,
        selection_item_keys=selection_item_keys,
        provenance=provenance,
        item_count=row.item_count,
        fingerprint=row.fingerprint,
    )


def _fingerprint_dataset_items(items: tuple[EvalDatasetItem, ...]) -> str:
    digest_input = "|".join(
        f"{item.item_key}:{Path(item.path).resolve()}:{json.dumps(item.labels, sort_keys=True)}"
        for item in items
    )
    return hashlib.sha1(digest_input.encode("utf-8")).hexdigest()


def _fingerprint_slice_items(
    dataset: EvalDatasetDefinition,
    selection_item_keys: tuple[str, ...],
) -> str:
    item_map = {item.item_key: item for item in dataset.items}
    digest_input = "|".join(
        f"{item_key}:{Path(item_map[item_key].path).resolve()}"
        for item_key in selection_item_keys
    )
    return hashlib.sha1(digest_input.encode("utf-8")).hexdigest()


def _eval_dataset_tables_exist(db: Session) -> bool:
    inspector = inspect(db.bind)
    table_names = set(inspector.get_table_names())
    return {"eval_datasets", "eval_dataset_slices"}.issubset(table_names)


def _require_eval_dataset_tables(db: Session) -> None:
    if not _eval_dataset_tables_exist(db):
        raise EvalDatasetError(
            "Eval dataset registry is unavailable until database migrations have been applied."
        )
