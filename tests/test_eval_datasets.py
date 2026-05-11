from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from train_api.main import create_eval_dataset_route, create_eval_dataset_slice_route
from train_core.datasets import (
    create_eval_dataset,
    create_eval_dataset_slice,
    delete_eval_dataset,
    get_eval_dataset,
    get_eval_dataset_slice,
    list_eval_datasets,
    resolve_eval_dataset_paths,
)
from train_core.db import SessionLocal, init_db
from train_core.schemas import EvalDatasetSliceWrite, EvalDatasetWrite
from train_core.trinity_reply_policy_service import propose_reply_policy_from_bundle_files
from train_core.trinity_spot_policy_service import propose_spot_review_policy_from_bundle_files


def _reply_bundle_payload() -> dict[str, object]:
    return {
        "bundle_id": "bundle-1",
        "bundle_type": "tone-learning",
        "exported_at": datetime(2026, 5, 3, 12, 0, tzinfo=UTC).isoformat(),
        "thread_snapshot": {
            "company_id": "company-1",
            "thread_ref": "reply:linkedin:alice",
            "channel": "linkedin",
            "contact_handle": "linkedin://alice",
            "latest_inbound_text": "Can you send the update?",
            "requested_at": datetime(2026, 5, 3, 11, 59, tzinfo=UTC).isoformat(),
            "messages": (),
            "context_snippets": (),
            "golden_examples": (),
            "metadata": {"source_product": "reply"},
            "contract_version": "trinity.reply.v1alpha1",
        },
        "evidence_units": (),
        "ranked_draft_set": {
            "cycle_id": "cycle-1",
            "thread_ref": "reply:linkedin:alice",
            "channel": "linkedin",
            "generated_at": datetime(2026, 5, 3, 12, 0, tzinfo=UTC).isoformat(),
            "drafts": (
                {
                    "company_id": "company-1",
                    "candidate_id": "candidate-1",
                    "thread_ref": "reply:linkedin:alice",
                    "recipient_handle": "linkedin://alice",
                    "channel": "linkedin",
                    "rank": 1,
                    "draft_text": "Draft text",
                    "rationale": "Best current action.",
                    "risk_flags": (),
                    "delivery_eligible": True,
                    "scores": {
                        "impact": 8,
                        "confidence": 7,
                        "ease": 6,
                        "quality_score": 84.0,
                        "urgency_score": 80.0,
                        "freshness_score": 79.0,
                        "feedback_score": 25.0,
                    },
                    "source_evidence_ids": ("evidence-1",),
                    "candidate_type": "ACTION",
                    "contract_version": "trinity.reply.v1alpha1",
                },
            ),
            "accepted_artifact_version": {
                "artifact_key": "reply_ranker_policy",
                "version": "reply_ranker_policy.v0",
                "source_project": "trinity",
                "accepted_at": datetime(2026, 5, 3, 12, 0, tzinfo=UTC).isoformat(),
            },
            "trace_ref": "exports/cycle-1.json",
            "contract_version": "trinity.reply.v1alpha1",
        },
        "selected_candidate_id": "candidate-1",
        "draft_outcome_event": {
            "company_id": "company-1",
            "cycle_id": "cycle-1",
            "thread_ref": "reply:linkedin:alice",
            "channel": "linkedin",
            "disposition": "EDITED_THEN_SENT",
            "occurred_at": datetime(2026, 5, 3, 12, 1, tzinfo=UTC).isoformat(),
            "candidate_id": "candidate-1",
            "original_draft_text": "Draft text",
            "final_text": "Thanks Alice. I can send the update today.",
            "edit_distance": 0.2,
            "latency_ms": 1000,
            "send_result": "ok",
            "notes": "fixture",
        },
        "labels": {"slice": "tone"},
        "contract_version": "trinity.reply.v1alpha1",
    }


def _spot_bundle_payload() -> dict[str, object]:
    return {
        "bundle_id": "spot-bundle-1",
        "bundle_type": "spot-review-policy-learning",
        "exported_at": datetime(2026, 5, 9, 12, 0, tzinfo=UTC).isoformat(),
        "spot_reasoning_request": {
            "company_id": "company-1",
            "run_id": "run-1",
            "row_ref": "sheet1:42",
            "language": "de",
            "message_text": "Sample row",
            "occurred_at": datetime(2026, 5, 9, 12, 0, tzinfo=UTC).isoformat(),
            "metadata": {},
            "contract_version": "trinity.spot.v1alpha1",
        },
        "spot_reasoning_result": {
            "company_id": "company-1",
            "run_id": "run-1",
            "row_ref": "sheet1:42",
            "generated_at": datetime(2026, 5, 9, 12, 0, tzinfo=UTC).isoformat(),
            "candidates": (
                {
                    "candidate_key": "benign",
                    "interpretation": "Sample",
                    "rationale": "Sample",
                    "threat_label_hint": "Not Antisemitic",
                    "review_recommended": False,
                },
            ),
            "selected_candidate_key": "benign",
            "confidence_bundle": {
                "generator_confidence": 0.76,
                "refiner_confidence": 0.76,
                "evaluator_confidence": 0.76,
                "frontier_confidence": 0.76,
                "combined_confidence": 0.76,
                "disagreement_severity": 0.1,
            },
            "review_required": False,
            "review_reason": "fixture",
            "policy_sensitive": False,
            "automatic_disposition": "auto_approve",
            "human_override_allowed": True,
            "deeper_analysis_available": True,
            "escalation_recommended": False,
            "contract_version": "trinity.spot.v1alpha1",
        },
        "spot_review_outcome": {
            "company_id": "company-1",
            "cycle_id": "cycle-1",
            "run_id": "run-1",
            "row_ref": "sheet1:42",
            "selected_candidate_key": "benign",
            "disposition": "CONFIRMED_NEGATIVE",
            "final_label": "Not Antisemitic",
            "occurred_at": datetime(2026, 5, 9, 12, 1, tzinfo=UTC).isoformat(),
            "reviewer_notes": "fixture",
            "metadata": {},
            "contract_version": "trinity.spot.v1alpha1",
        },
        "labels": {"bundle_type": "spot-review-policy-learning"},
        "contract_version": "trinity.spot.v1alpha1",
    }


def test_eval_dataset_registry_crud_and_slice_resolution(tmp_path: Path) -> None:
    init_db()
    dataset_key = "test-reply-dataset"
    dataset_version = "2026-05-11.1"
    slice_key = "company-regression"
    slice_version = "2026-05-11.1"
    bundle_path_a = tmp_path / "bundle-a.json"
    bundle_path_b = tmp_path / "bundle-b.json"
    bundle_path_a.write_text(json.dumps({"bundle": _reply_bundle_payload()}, indent=2), encoding="utf-8")
    bundle_payload_b = _reply_bundle_payload()
    bundle_payload_b["bundle_id"] = "bundle-2"
    bundle_payload_b["thread_snapshot"]["thread_ref"] = "reply:linkedin:bob"
    bundle_payload_b["ranked_draft_set"]["cycle_id"] = "cycle-2"
    bundle_payload_b["ranked_draft_set"]["thread_ref"] = "reply:linkedin:bob"
    bundle_payload_b["draft_outcome_event"]["cycle_id"] = "cycle-2"
    bundle_payload_b["draft_outcome_event"]["thread_ref"] = "reply:linkedin:bob"
    bundle_path_b.write_text(json.dumps({"bundle": bundle_payload_b}, indent=2), encoding="utf-8")

    with SessionLocal() as db:
        if get_eval_dataset(dataset_key, dataset_version, db) is not None:
            delete_eval_dataset(db, dataset_key, dataset_version)

        dataset = create_eval_dataset(
            db,
            EvalDatasetWrite(
                key=dataset_key,
                version=dataset_version,
                name="Reply Eval Dataset",
                description="Fixture reply corpus for dataset registry tests.",
                source_kind="trinity-reply",
                scope_kind="company",
                scope_value="company-1",
                items=(
                    {
                        "item_key": "bundle-a",
                        "path": str(bundle_path_a.resolve()),
                        "labels": {"slice": "tone"},
                    },
                    {
                        "item_key": "bundle-b",
                        "path": str(bundle_path_b.resolve()),
                        "labels": {"slice": "tone"},
                    },
                ),
                provenance={"export_family": "tone-learning"},
            ),
        )
        assert dataset.item_count == 2
        assert dataset.ref == f"{dataset_key}@{dataset_version}"
        assert len(list_eval_datasets(db)) >= 1

        slice_definition = create_eval_dataset_slice(
            db,
            dataset_key,
            dataset_version,
            EvalDatasetSliceWrite(
                key=slice_key,
                version=slice_version,
                name="Reply Regression Slice",
                description="Single-item regression slice.",
                scope_kind="company",
                scope_value="company-1",
                selection_item_keys=("bundle-b",),
                provenance={"purpose": "regression"},
            ),
        )
        assert slice_definition.item_count == 1
        assert get_eval_dataset_slice(dataset_key, dataset_version, slice_key, slice_version, db) is not None

        dataset_paths = resolve_eval_dataset_paths(
            dataset_key=dataset_key,
            dataset_version=dataset_version,
            db=db,
        )
        assert dataset_paths == (str(bundle_path_a.resolve()), str(bundle_path_b.resolve()))

        slice_paths = resolve_eval_dataset_paths(
            dataset_key=dataset_key,
            dataset_version=dataset_version,
            slice_key=slice_key,
            slice_version=slice_version,
            db=db,
        )
        assert slice_paths == (str(bundle_path_b.resolve()),)

        delete_eval_dataset(db, dataset_key, dataset_version)
        assert get_eval_dataset(dataset_key, dataset_version, db) is None


def test_eval_dataset_routes_create_dataset_and_slice(tmp_path: Path) -> None:
    init_db()
    dataset_key = "test-route-dataset"
    dataset_version = "2026-05-11.1"
    slice_key = "hard-cases"
    slice_version = "2026-05-11.1"
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps({"bundle": _reply_bundle_payload()}, indent=2), encoding="utf-8")

    with SessionLocal() as db:
        if get_eval_dataset(dataset_key, dataset_version, db) is not None:
            delete_eval_dataset(db, dataset_key, dataset_version)

        dataset = create_eval_dataset_route(
            EvalDatasetWrite(
                key=dataset_key,
                version=dataset_version,
                name="Route Dataset",
                description="Route-created dataset.",
                source_kind="trinity-reply",
                scope_kind="company",
                scope_value="company-1",
                items=(
                    {
                        "item_key": "bundle-1",
                        "path": str(bundle_path.resolve()),
                        "labels": {"slice": "tone"},
                    },
                ),
                provenance={"route": True},
            ),
            db=db,
        )
        assert dataset.item_count == 1

        slice_read = create_eval_dataset_slice_route(
            dataset_key,
            dataset_version,
            EvalDatasetSliceWrite(
                key=slice_key,
                version=slice_version,
                name="Hard Cases",
                description="Route-created slice.",
                scope_kind="company",
                scope_value="company-1",
                selection_item_keys=("bundle-1",),
                provenance={"kind": "hard-case"},
            ),
            db=db,
        )
        assert slice_read.dataset_ref == f"{dataset_key}@{dataset_version}"

        delete_eval_dataset(db, dataset_key, dataset_version)


def test_reply_policy_can_load_bundle_files_from_registered_dataset(tmp_path: Path) -> None:
    init_db()
    dataset_key = "reply-proposal-dataset"
    dataset_version = "2026-05-11.1"
    bundle_path = tmp_path / "reply-bundle.json"
    bundle_path.write_text(json.dumps({"bundle": _reply_bundle_payload()}, indent=2), encoding="utf-8")

    with SessionLocal() as db:
        if get_eval_dataset(dataset_key, dataset_version, db) is not None:
            delete_eval_dataset(db, dataset_key, dataset_version)
        create_eval_dataset(
            db,
            EvalDatasetWrite(
                key=dataset_key,
                version=dataset_version,
                name="Reply Proposal Dataset",
                description="Reply proposal dataset.",
                source_kind="trinity-reply",
                scope_kind="company",
                scope_value="company-1",
                items=(
                    {
                        "item_key": "bundle-1",
                        "path": str(bundle_path.resolve()),
                        "labels": {"slice": "tone"},
                    },
                ),
                provenance={"purpose": "proposal"},
            ),
        )

    result = propose_reply_policy_from_bundle_files(
        learner_kind="tone",
        eval_dataset_key=dataset_key,
        eval_dataset_version=dataset_version,
    )

    assert result.bundle_count == 1
    assert result.proposal.scope_kind == "company"

    with SessionLocal() as db:
        delete_eval_dataset(db, dataset_key, dataset_version)


def test_spot_policy_can_load_bundle_files_from_registered_slice(tmp_path: Path) -> None:
    init_db()
    dataset_key = "spot-proposal-dataset"
    dataset_version = "2026-05-11.1"
    slice_key = "company-slice"
    slice_version = "2026-05-11.1"
    bundle_path = tmp_path / "spot-bundle.json"
    bundle_path.write_text(json.dumps({"bundle": _spot_bundle_payload()}, indent=2), encoding="utf-8")

    with SessionLocal() as db:
        if get_eval_dataset(dataset_key, dataset_version, db) is not None:
            delete_eval_dataset(db, dataset_key, dataset_version)
        create_eval_dataset(
            db,
            EvalDatasetWrite(
                key=dataset_key,
                version=dataset_version,
                name="Spot Proposal Dataset",
                description="Spot proposal dataset.",
                source_kind="trinity-spot",
                scope_kind="company",
                scope_value="company-1",
                items=(
                    {
                        "item_key": "spot-row-1",
                        "path": str(bundle_path.resolve()),
                        "labels": {"slice": "review"},
                    },
                ),
                provenance={"purpose": "proposal"},
            ),
        )
        create_eval_dataset_slice(
            db,
            dataset_key,
            dataset_version,
            EvalDatasetSliceWrite(
                key=slice_key,
                version=slice_version,
                name="Spot Company Slice",
                description="Single-row spot slice.",
                scope_kind="company",
                scope_value="company-1",
                selection_item_keys=("spot-row-1",),
                provenance={"kind": "company"},
            ),
        )

    result = propose_spot_review_policy_from_bundle_files(
        learner_kind="review-policy",
        eval_dataset_key=dataset_key,
        eval_dataset_version=dataset_version,
        eval_dataset_slice_key=slice_key,
        eval_dataset_slice_version=slice_version,
    )

    assert result.bundle_count == 1
    assert result.proposal.scope_kind == "company"

    with SessionLocal() as db:
        delete_eval_dataset(db, dataset_key, dataset_version)
