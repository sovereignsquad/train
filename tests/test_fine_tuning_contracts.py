from __future__ import annotations

from dataclasses import dataclass
import json
from datetime import UTC, datetime
from pathlib import Path
import subprocess

from train_api.main import (
    create_adapter_artifact_route,
    create_training_spec_route,
    get_training_spec_readiness,
    package_adapter_artifact_for_ollama_route,
    run_self_learning_cycle_route,
    run_training_spec_route,
)
from train_core.cli import main as train_cli_main
from train_core.comparison import StandardComparisonRow, build_standard_comparison_report
from train_core.datasets import create_eval_dataset, delete_eval_dataset, get_eval_dataset
from train_core.db import SessionLocal, init_db
from train_core.fine_tuning import (
    create_adapter_artifact,
    create_training_spec,
    delete_adapter_artifact,
    delete_training_spec,
    get_adapter_artifact,
    get_training_spec,
)
from train_core.health import HealthCheckResult, HealthReport
from train_core.models import MetricDirection
from train_core.grader_suites import create_grader_suite
from train_core import mlx_lm_worker
from train_core.ollama_packaging import package_adapter_artifact_for_ollama
from train_core import self_learning_cycle
from train_core.schemas import (
    AdapterArtifactRead,
    AdapterArtifactWrite,
    EvalDatasetWrite,
    GraderSuiteWrite,
    OllamaPackageRequest,
    SelfLearningCycleRead,
    SelfLearningCycleRequest,
    TrainingSpecRunRead,
    TrainingSpecRunRequest,
    TrainingSpecWrite,
    TrainingReadinessRead,
)


def test_training_spec_and_adapter_artifact_contracts_persist(tmp_path: Path) -> None:
    init_db()
    dataset_key = "ft-dataset"
    dataset_version = "2026-05-13.1"
    suite_key = "ft-suite"
    suite_version = "2026-05-13.1"
    spec_key = "reply-sft"
    spec_version = "2026-05-13.1"
    artifact_key = "reply-adapter"
    artifact_version = "2026-05-13.1"
    corpus_file = tmp_path / "train.jsonl"
    corpus_file.write_text("{}\n", encoding="utf-8")
    adapter_file = tmp_path / "adapters.safetensors"
    adapter_file.write_text("fixture", encoding="utf-8")
    log_file = tmp_path / "train.log"
    log_file.write_text("fixture", encoding="utf-8")
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()

    with SessionLocal() as db:
        if get_eval_dataset(dataset_key, dataset_version, db) is not None:
            delete_eval_dataset(db, dataset_key, dataset_version)
        if get_training_spec(spec_key, spec_version, db) is not None:
            delete_training_spec(db, spec_key, spec_version)
        create_eval_dataset(
            db,
            EvalDatasetWrite(
                key=dataset_key,
                version=dataset_version,
                name="Fine Tuning Dataset",
                description="Fixture dataset for training spec tests.",
                source_kind="trinity-reply",
                scope_kind="company",
                scope_value="company-1",
                items=(
                    {
                        "item_key": "train-1",
                        "path": str(corpus_file.resolve()),
                        "labels": {"partition": "train"},
                    },
                ),
                provenance={"purpose": "fine-tuning"},
            ),
        )
        create_grader_suite(
            db,
            dataset_key,
            dataset_version,
            GraderSuiteWrite(
                key=suite_key,
                version=suite_version,
                name="Fine Tuning Suite",
                description="Fixture suite for training contracts.",
                proposal_family="reply_adapter",
                graders=(
                    {
                        "grader_key": "sample_count",
                        "grader_kind": "code",
                        "entrypoint_ref": "builtin://minimum-sample-count",
                        "metric_name": "sample_count",
                        "pass_threshold": 1,
                    },
                ),
                provenance={"owner": "tests"},
            ),
        )

        training_spec = create_training_spec(
            db,
            TrainingSpecWrite(
                key=spec_key,
                version=spec_version,
                name="Reply SFT Spec",
                description="Apple Silicon MLX-LM contract fixture.",
                dataset_key=dataset_key,
                dataset_version=dataset_version,
                grader_suite_key=suite_key,
                grader_suite_version=suite_version,
                base_model_ref="mlx-community/Llama-3.2-3B-Instruct-4bit",
                template_ref="chatml://reply-v1",
                tokenizer_ref="hf://meta-llama/Llama-3.2-3B-Instruct",
                training_backend="mlx-lm",
                training_stage="sft",
                training_method="qlora",
                expected_adapter_family="reply_adapter",
                output_dir=str(output_dir.resolve()),
                hyperparameters={"iters": 100, "batch_size": 2},
                provenance={"owner": "tests"},
            ),
        )
        assert training_spec.ref == f"{spec_key}@{spec_version}"
        assert training_spec.dataset_ref == f"{dataset_key}@{dataset_version}"
        assert training_spec.grader_suite_ref == (
            f"{dataset_key}@{dataset_version}:{suite_key}@{suite_version}"
        )
        assert training_spec.base_model_source_kind == "huggingface"
        assert get_training_spec(spec_key, spec_version, db) is not None

        artifact = create_adapter_artifact(
            db,
            AdapterArtifactWrite(
                key=artifact_key,
                version=artifact_version,
                training_spec_key=spec_key,
                training_spec_version=spec_version,
                name="Reply Adapter",
                description="Fixture adapter artifact.",
                adapter_format="safetensors",
                artifact_path=str(adapter_file.resolve()),
                training_log_path=str(log_file.resolve()),
                provenance={"round": "fixture"},
            ),
        )
        assert artifact.training_spec_ref == f"{spec_key}@{spec_version}"
        assert artifact.adapter_family == "reply_adapter"
        assert artifact.training_backend == "mlx-lm"
        assert artifact.base_model_source_kind == "huggingface"
        assert get_adapter_artifact(artifact_key, artifact_version, db) is not None

        delete_training_spec(db, spec_key, spec_version)
        assert get_training_spec(spec_key, spec_version, db) is None
        assert get_adapter_artifact(artifact_key, artifact_version, db) is None
        delete_eval_dataset(db, dataset_key, dataset_version)


def _write_reply_adapter_comparison_report(path: Path) -> Path:
    report = build_standard_comparison_report(
        report_id="reply-adapter.comparison",
        generated_at=datetime(2026, 5, 19, 10, 0, tzinfo=UTC),
        evaluation_mode="fixed_replay_corpus",
        metric_name="reply_adapter_fit",
        metric_direction=MetricDirection.MAXIMIZE,
        sample_count=8,
        corpus_fingerprint="replyadapter123",
        rows=[
            StandardComparisonRow(
                label="baseline",
                artifact_key="reply_adapter",
                version="baseline.v1",
                score=0.71,
                status="evaluated",
                notes="fixture baseline",
            ),
            StandardComparisonRow(
                label="incumbent",
                artifact_key="reply_adapter",
                version="incumbent.v1",
                score=0.75,
                status="evaluated",
                notes="fixture incumbent",
            ),
            StandardComparisonRow(
                label="candidate",
                artifact_key="reply_adapter",
                version="candidate.v2",
                score=0.83,
                status="evaluated",
                notes="fixture candidate",
            ),
        ],
        summary="Fixture comparison for reply adapter tests.",
    )
    path.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
    return path


def test_training_spec_and_adapter_artifact_routes(tmp_path: Path) -> None:
    init_db()
    dataset_key = "ft-route-dataset"
    dataset_version = "2026-05-13.1"
    suite_key = "ft-route-suite"
    suite_version = "2026-05-13.1"
    spec_key = "route-spec"
    spec_version = "2026-05-13.1"
    corpus_file = tmp_path / "train.jsonl"
    corpus_file.write_text("{}\n", encoding="utf-8")
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    adapter_file = tmp_path / "adapter.gguf"
    adapter_file.write_text("fixture", encoding="utf-8")

    with SessionLocal() as db:
        if get_eval_dataset(dataset_key, dataset_version, db) is not None:
            delete_eval_dataset(db, dataset_key, dataset_version)
        if get_adapter_artifact("route-artifact", "2026-05-13.1", db) is not None:
            delete_adapter_artifact(db, "route-artifact", "2026-05-13.1")
        if get_training_spec(spec_key, spec_version, db) is not None:
            delete_training_spec(db, spec_key, spec_version)
        create_eval_dataset(
            db,
            EvalDatasetWrite(
                key=dataset_key,
                version=dataset_version,
                name="Route Dataset",
                description="Fixture route dataset.",
                source_kind="trinity-reply",
                scope_kind="company",
                scope_value="company-1",
                items=(
                    {
                        "item_key": "train-1",
                        "path": str(corpus_file.resolve()),
                        "labels": {"partition": "train"},
                    },
                ),
                provenance={"purpose": "route"},
            ),
        )
        create_grader_suite(
            db,
            dataset_key,
            dataset_version,
            GraderSuiteWrite(
                key=suite_key,
                version=suite_version,
                name="Route Suite",
                description="Fixture route suite.",
                proposal_family="reply_adapter",
                graders=(
                    {
                        "grader_key": "sample_count",
                        "grader_kind": "code",
                        "entrypoint_ref": "builtin://minimum-sample-count",
                        "metric_name": "sample_count",
                        "pass_threshold": 1,
                    },
                ),
                provenance={"kind": "route"},
            ),
        )

        spec = create_training_spec_route(
            TrainingSpecWrite(
                key=spec_key,
                version=spec_version,
                name="Route Spec",
                description="Route-created training spec.",
                dataset_key=dataset_key,
                dataset_version=dataset_version,
                grader_suite_key=suite_key,
                grader_suite_version=suite_version,
                base_model_ref="mlx-community/Llama-3.2-3B-Instruct-4bit",
                template_ref="chatml://reply-v1",
                tokenizer_ref="hf://meta-llama/Llama-3.2-3B-Instruct",
                training_backend="mlx-lm",
                training_stage="sft",
                training_method="qlora",
                expected_adapter_family="reply_adapter",
                output_dir=str(output_dir.resolve()),
                hyperparameters={"iters": 50},
                provenance={"kind": "route"},
            ),
            db=db,
        )
        assert spec.training_backend == "mlx-lm"
        assert spec.base_model_source_kind == "huggingface"

        artifact = create_adapter_artifact_route(
            AdapterArtifactWrite(
                key="route-artifact",
                version="2026-05-13.1",
                training_spec_key=spec_key,
                training_spec_version=spec_version,
                name="Route Artifact",
                description="Route-created adapter artifact.",
                adapter_format="gguf",
                artifact_path=str(adapter_file.resolve()),
                provenance={"kind": "route"},
            ),
            db=db,
        )
        assert artifact.adapter_format == "gguf"
        assert artifact.training_spec_ref == f"{spec_key}@{spec_version}"
        assert artifact.base_model_source_kind == "huggingface"

        delete_eval_dataset(db, dataset_key, dataset_version)


def test_package_adapter_artifact_for_ollama_persists_metadata(tmp_path: Path) -> None:
    init_db()
    dataset_key = "package-dataset"
    dataset_version = "2026-05-19.1"
    suite_key = "package-suite"
    suite_version = "2026-05-19.1"
    spec_key = "package-spec"
    spec_version = "2026-05-19.1"
    artifact_key = "package-artifact"
    artifact_version = "2026-05-19.1"
    corpus_file = tmp_path / "train.jsonl"
    corpus_file.write_text("{}\n", encoding="utf-8")
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()
    adapter_file = adapter_dir / "adapters.safetensors"
    adapter_file.write_text("fixture", encoding="utf-8")

    with SessionLocal() as db:
        if get_eval_dataset(dataset_key, dataset_version, db) is not None:
            delete_eval_dataset(db, dataset_key, dataset_version)
        if get_training_spec(spec_key, spec_version, db) is not None:
            delete_training_spec(db, spec_key, spec_version)
        create_eval_dataset(
            db,
            EvalDatasetWrite(
                key=dataset_key,
                version=dataset_version,
                name="Package Dataset",
                description="Fixture dataset for Ollama packaging tests.",
                source_kind="trinity-reply",
                scope_kind="company",
                scope_value="company-1",
                items=(
                    {
                        "item_key": "train-row",
                        "path": str(corpus_file.resolve()),
                        "labels": {"partition": "train"},
                    },
                ),
                provenance={"purpose": "packaging"},
            ),
        )
        create_grader_suite(
            db,
            dataset_key,
            dataset_version,
            GraderSuiteWrite(
                key=suite_key,
                version=suite_version,
                name="Package Suite",
                description="Fixture suite for packaging tests.",
                proposal_family="reply_adapter",
                graders=(
                    {
                        "grader_key": "sample_count",
                        "grader_kind": "code",
                        "entrypoint_ref": "builtin://minimum-sample-count",
                        "metric_name": "sample_count",
                        "pass_threshold": 1,
                    },
                ),
                provenance={"owner": "tests"},
            ),
        )
        create_training_spec(
            db,
            TrainingSpecWrite(
                key=spec_key,
                version=spec_version,
                name="Package Spec",
                description="Fixture training spec for packaging tests.",
                dataset_key=dataset_key,
                dataset_version=dataset_version,
                grader_suite_key=suite_key,
                grader_suite_version=suite_version,
                base_model_ref="mlx-community/Llama-3.2-3B-Instruct-4bit",
                template_ref="chatml://reply-v1",
                tokenizer_ref="hf://meta-llama/Llama-3.2-3B-Instruct",
                training_backend="mlx-lm",
                training_stage="sft",
                training_method="qlora",
                expected_adapter_family="reply_adapter",
                output_dir=str(output_dir.resolve()),
                hyperparameters={"iters": 10},
                provenance={"owner": "tests"},
            ),
        )
        create_adapter_artifact(
            db,
            AdapterArtifactWrite(
                key=artifact_key,
                version=artifact_version,
                training_spec_key=spec_key,
                training_spec_version=spec_version,
                name="Package Artifact",
                description="Fixture adapter artifact for packaging tests.",
                adapter_format="safetensors",
                artifact_path=str(adapter_file.resolve()),
                provenance={"owner": "tests"},
            ),
        )

        result = package_adapter_artifact_for_ollama(
            artifact_key=artifact_key,
            artifact_version=artifact_version,
            ollama_model_name="train-reply-adapter:test",
            temperature=0.2,
            top_p=0.9,
            system_prompt="Use a concise reply style.",
            db=db,
        )

        metadata_payload = json.loads(Path(result.metadata_path).read_text(encoding="utf-8"))
        modelfile_text = Path(result.modelfile_path).read_text(encoding="utf-8")

        assert Path(result.metadata_path).exists()
        assert Path(result.modelfile_path).exists()
        assert metadata_payload["ollama_model_name"] == "train-reply-adapter:test"
        assert metadata_payload["adapter_artifact_ref"] == f"{artifact_key}@{artifact_version}"
        assert "FROM mlx-community/Llama-3.2-3B-Instruct-4bit" in modelfile_text
        assert "ADAPTER" in modelfile_text
        assert 'SYSTEM "Use a concise reply style."' in modelfile_text
        assert result.adapter_artifact.packaging_metadata_path == result.metadata_path

        delete_eval_dataset(db, dataset_key, dataset_version)


def test_package_adapter_artifact_for_ollama_route(tmp_path: Path) -> None:
    init_db()
    dataset_key = "package-route-dataset"
    dataset_version = "2026-05-19.1"
    suite_key = "package-route-suite"
    suite_version = "2026-05-19.1"
    spec_key = "package-route-spec"
    spec_version = "2026-05-19.1"
    artifact_key = "package-route-artifact"
    artifact_version = "2026-05-19.1"
    corpus_file = tmp_path / "train.jsonl"
    corpus_file.write_text("{}\n", encoding="utf-8")
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    adapter_file = tmp_path / "adapters.safetensors"
    adapter_file.write_text("fixture", encoding="utf-8")

    with SessionLocal() as db:
        if get_eval_dataset(dataset_key, dataset_version, db) is not None:
            delete_eval_dataset(db, dataset_key, dataset_version)
        if get_adapter_artifact(artifact_key, artifact_version, db) is not None:
            delete_adapter_artifact(db, artifact_key, artifact_version)
        if get_training_spec(spec_key, spec_version, db) is not None:
            delete_training_spec(db, spec_key, spec_version)
        create_eval_dataset(
            db,
            EvalDatasetWrite(
                key=dataset_key,
                version=dataset_version,
                name="Package Route Dataset",
                description="Fixture dataset for packaging route tests.",
                source_kind="trinity-reply",
                scope_kind="company",
                scope_value="company-1",
                items=(
                    {
                        "item_key": "train-row",
                        "path": str(corpus_file.resolve()),
                        "labels": {"partition": "train"},
                    },
                ),
                provenance={"purpose": "packaging-route"},
            ),
        )
        create_grader_suite(
            db,
            dataset_key,
            dataset_version,
            GraderSuiteWrite(
                key=suite_key,
                version=suite_version,
                name="Package Route Suite",
                description="Fixture suite for packaging route tests.",
                proposal_family="reply_adapter",
                graders=(
                    {
                        "grader_key": "sample_count",
                        "grader_kind": "code",
                        "entrypoint_ref": "builtin://minimum-sample-count",
                        "metric_name": "sample_count",
                        "pass_threshold": 1,
                    },
                ),
                provenance={"owner": "tests"},
            ),
        )
        create_training_spec(
            db,
            TrainingSpecWrite(
                key=spec_key,
                version=spec_version,
                name="Package Route Spec",
                description="Fixture training spec for packaging route tests.",
                dataset_key=dataset_key,
                dataset_version=dataset_version,
                grader_suite_key=suite_key,
                grader_suite_version=suite_version,
                base_model_ref="mlx-community/Llama-3.2-3B-Instruct-4bit",
                template_ref="chatml://reply-v1",
                tokenizer_ref="hf://meta-llama/Llama-3.2-3B-Instruct",
                training_backend="mlx-lm",
                training_stage="sft",
                training_method="qlora",
                expected_adapter_family="reply_adapter",
                output_dir=str(output_dir.resolve()),
                hyperparameters={"iters": 10},
                provenance={"owner": "tests"},
            ),
        )
        create_adapter_artifact(
            db,
            AdapterArtifactWrite(
                key=artifact_key,
                version=artifact_version,
                training_spec_key=spec_key,
                training_spec_version=spec_version,
                name="Package Route Artifact",
                description="Fixture route adapter artifact.",
                adapter_format="safetensors",
                artifact_path=str(adapter_file.resolve()),
                provenance={"owner": "tests"},
            ),
        )

        result = package_adapter_artifact_for_ollama_route(
            artifact_key,
            artifact_version,
            OllamaPackageRequest(
                ollama_model_name="train-reply-adapter:route",
                system_prompt="Stay compact.",
            ),
            db=db,
        )

        assert result.ollama_model_name == "train-reply-adapter:route"
        assert Path(result.modelfile_path).exists()
        assert result.adapter_artifact.ref == f"{artifact_key}@{artifact_version}"

        delete_eval_dataset(db, dataset_key, dataset_version)


def test_mlx_lm_worker_route_and_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    init_db()
    dataset_key = "mlx-worker-dataset"
    dataset_version = "2026-05-13.1"
    suite_key = "mlx-worker-suite"
    suite_version = "2026-05-13.1"
    spec_key = "mlx-worker-spec"
    spec_version = "2026-05-13.1"
    train_file = tmp_path / "train.jsonl"
    valid_file = tmp_path / "valid.jsonl"
    test_file = tmp_path / "test.jsonl"
    train_file.write_text(json.dumps({"messages": [{"role": "user", "content": "Hi"}]}) + "\n", encoding="utf-8")
    valid_file.write_text(json.dumps({"messages": [{"role": "user", "content": "Check"}]}) + "\n", encoding="utf-8")
    test_file.write_text(json.dumps({"messages": [{"role": "user", "content": "Test"}]}) + "\n", encoding="utf-8")
    output_dir = tmp_path / "worker-output"
    output_dir.mkdir()

    def fake_run(command, capture_output, text, check):
        adapter_dir = Path(command[command.index("--adapter-path") + 1])
        adapter_dir.mkdir(parents=True, exist_ok=True)
        (adapter_dir / "adapters.safetensors").write_text("fixture", encoding="utf-8")
        data_dir = Path(command[command.index("--data") + 1])
        assert (data_dir / "train.jsonl").exists()
        assert (data_dir / "valid.jsonl").exists()
        assert (data_dir / "test.jsonl").exists()
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr(mlx_lm_worker.subprocess, "run", fake_run)
    monkeypatch.setattr(mlx_lm_worker, "assert_training_lane_ready", lambda spec: None)

    with SessionLocal() as db:
        if get_eval_dataset(dataset_key, dataset_version, db) is not None:
            delete_eval_dataset(db, dataset_key, dataset_version)
        if get_training_spec(spec_key, spec_version, db) is not None:
            delete_training_spec(db, spec_key, spec_version)
        create_eval_dataset(
            db,
            EvalDatasetWrite(
                key=dataset_key,
                version=dataset_version,
                name="MLX Worker Dataset",
                description="Fixture dataset for mlx-lm worker tests.",
                source_kind="trinity-reply",
                scope_kind="company",
                scope_value="company-1",
                items=(
                    {
                        "item_key": "train-row",
                        "path": str(train_file.resolve()),
                        "labels": {"partition": "train"},
                    },
                    {
                        "item_key": "valid-row",
                        "path": str(valid_file.resolve()),
                        "labels": {"partition": "valid"},
                    },
                    {
                        "item_key": "test-row",
                        "path": str(test_file.resolve()),
                        "labels": {"partition": "test"},
                    },
                ),
                provenance={"purpose": "mlx-worker"},
            ),
        )
        create_grader_suite(
            db,
            dataset_key,
            dataset_version,
            GraderSuiteWrite(
                key=suite_key,
                version=suite_version,
                name="MLX Worker Suite",
                description="Fixture suite for mlx-lm worker tests.",
                proposal_family="reply_adapter",
                graders=(
                    {
                        "grader_key": "sample_count",
                        "grader_kind": "code",
                        "entrypoint_ref": "builtin://minimum-sample-count",
                        "metric_name": "sample_count",
                        "pass_threshold": 1,
                    },
                ),
                provenance={"owner": "tests"},
            ),
        )
        create_training_spec(
            db,
            TrainingSpecWrite(
                key=spec_key,
                version=spec_version,
                name="MLX Worker Spec",
                description="Fixture training spec for mlx-lm worker tests.",
                dataset_key=dataset_key,
                dataset_version=dataset_version,
                grader_suite_key=suite_key,
                grader_suite_version=suite_version,
                base_model_ref="mlx-community/Llama-3.2-3B-Instruct-4bit",
                template_ref="chatml://reply-v1",
                tokenizer_ref="hf://meta-llama/Llama-3.2-3B-Instruct",
                training_backend="mlx-lm",
                training_stage="sft",
                training_method="qlora",
                expected_adapter_family="reply_adapter",
                output_dir=str(output_dir.resolve()),
                hyperparameters={"iters": 5, "batch_size": 1},
                provenance={"owner": "tests"},
            ),
        )

        route_result = run_training_spec_route(
            spec_key,
            spec_version,
            TrainingSpecRunRequest(
                adapter_key="mlx-route-adapter",
                adapter_version="2026-05-13.1",
                adapter_name="MLX Route Adapter",
                adapter_description="Route-run adapter artifact.",
            ),
            db=db,
        )
        assert route_result.training_backend == "mlx-lm"
        assert Path(route_result.training_log_path).exists()
        assert route_result.adapter_artifact.artifact_path.endswith("adapters.safetensors")
        metadata_payload = json.loads(Path(route_result.metadata_path).read_text(encoding="utf-8"))
        assert metadata_payload["base_model_source_kind"] == "huggingface"
        assert metadata_payload["resolved_base_model_ref"] == "mlx-community/Llama-3.2-3B-Instruct-4bit"
        assert metadata_payload["resolved_base_model_path"] is None

    exit_code = train_cli_main(
        [
            "run-training-spec",
            "--spec-key",
            spec_key,
            "--spec-version",
            spec_version,
            "--adapter-key",
            "mlx-cli-adapter",
            "--adapter-version",
            "2026-05-13.2",
            "--adapter-name",
            "MLX CLI Adapter",
            "--adapter-description",
            "CLI-run adapter artifact.",
            "--output-format",
            "summary",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Ran mlx-lm training" in captured.out
    assert "mlx-cli-adapter@2026-05-13.2" in captured.out

    with SessionLocal() as db:
        delete_eval_dataset(db, dataset_key, dataset_version)


def test_run_daily_self_learning_cycle_packages_only_after_pass(
    tmp_path: Path,
    monkeypatch,
) -> None:
    init_db()
    dataset_key = "cycle-dataset"
    dataset_version = "2026-05-19.1"
    suite_key = "cycle-suite"
    suite_version = "2026-05-19.1"
    spec_key = "cycle-spec"
    spec_version = "2026-05-19.1"
    corpus_file = tmp_path / "train.jsonl"
    corpus_file.write_text("{}\n", encoding="utf-8")
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    comparison_path = _write_reply_adapter_comparison_report(tmp_path / "comparison.json")

    with SessionLocal() as db:
        if get_eval_dataset(dataset_key, dataset_version, db) is not None:
            delete_eval_dataset(db, dataset_key, dataset_version)
        if get_training_spec(spec_key, spec_version, db) is not None:
            delete_training_spec(db, spec_key, spec_version)
        create_eval_dataset(
            db,
            EvalDatasetWrite(
                key=dataset_key,
                version=dataset_version,
                name="Cycle Dataset",
                description="Fixture dataset for self-learning cycle tests.",
                source_kind="trinity-reply",
                scope_kind="company",
                scope_value="company-1",
                items=(
                    {
                        "item_key": "train-row",
                        "path": str(corpus_file.resolve()),
                        "labels": {"partition": "train"},
                    },
                ),
                provenance={"purpose": "self-learning"},
            ),
        )
        create_grader_suite(
            db,
            dataset_key,
            dataset_version,
            GraderSuiteWrite(
                key=suite_key,
                version=suite_version,
                name="Cycle Suite",
                description="Fixture suite for self-learning cycle tests.",
                proposal_family="reply_adapter",
                graders=(
                    {
                        "grader_key": "sample_count",
                        "grader_kind": "code",
                        "entrypoint_ref": "builtin://minimum-sample-count",
                        "metric_name": "sample_count",
                        "pass_threshold": 1,
                    },
                ),
                provenance={"owner": "tests"},
            ),
        )
        create_training_spec(
            db,
            TrainingSpecWrite(
                key=spec_key,
                version=spec_version,
                name="Cycle Spec",
                description="Fixture training spec for self-learning cycle tests.",
                dataset_key=dataset_key,
                dataset_version=dataset_version,
                grader_suite_key=suite_key,
                grader_suite_version=suite_version,
                base_model_ref="mlx-community/Llama-3.2-3B-Instruct-4bit",
                template_ref="chatml://reply-v1",
                tokenizer_ref="hf://meta-llama/Llama-3.2-3B-Instruct",
                training_backend="mlx-lm",
                training_stage="sft",
                training_method="qlora",
                expected_adapter_family="reply_adapter",
                output_dir=str(output_dir.resolve()),
                hyperparameters={"iters": 10},
                provenance={"owner": "tests"},
            ),
        )

    spec = get_training_spec(spec_key, spec_version)
    assert spec is not None

    monkeypatch.setattr(
        self_learning_cycle,
        "build_doctor_report",
        lambda **kwargs: HealthReport(
            workflow="training",
            generated_at="2026-05-19T10:00:00Z",
            overall_status="pass",
            ok=True,
            warning_count=0,
            failure_count=0,
            checks=(
                HealthCheckResult(
                    key="offline-training",
                    status="pass",
                    summary="ready",
                    details={},
                    remediation=None,
                ),
            ),
        ),
    )
    monkeypatch.setattr(
        self_learning_cycle,
        "check_training_lane_readiness",
        lambda **kwargs: HealthCheckResult(
            key="offline-training",
            status="pass",
            summary="ready",
            details={"training_spec_ref": spec.ref},
            remediation=None,
        ),
    )

    def fake_run_training_spec_with_mlx_lm(*, spec_key, spec_version, payload):
        adapter_artifact = AdapterArtifactRead(
            key=payload.adapter_key,
            version=payload.adapter_version,
            ref=f"{payload.adapter_key}@{payload.adapter_version}",
            training_spec_key=spec_key,
            training_spec_version=spec_version,
            training_spec_ref=f"{spec_key}@{spec_version}",
            name=payload.adapter_name,
            description=payload.adapter_description,
            dataset_key=dataset_key,
            dataset_version=dataset_version,
            dataset_ref=f"{dataset_key}@{dataset_version}",
            grader_suite_key=suite_key,
            grader_suite_version=suite_version,
            grader_suite_ref=f"{dataset_key}@{dataset_version}:{suite_key}@{suite_version}",
            base_model_ref="mlx-community/Llama-3.2-3B-Instruct-4bit",
            base_model_source_kind="huggingface",
            template_ref="chatml://reply-v1",
            tokenizer_ref="hf://meta-llama/Llama-3.2-3B-Instruct",
            training_backend="mlx-lm",
            training_stage="sft",
            training_method="qlora",
            adapter_family="reply_adapter",
            adapter_format="safetensors",
            artifact_path=str((tmp_path / "adapter" / "adapters.safetensors").resolve()),
            checkpoint_path=None,
            training_log_path=str((tmp_path / "train.log").resolve()),
            packaging_metadata_path=None,
            provenance={},
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        return TrainingSpecRunRead(
            training_spec_ref=f"{spec_key}@{spec_version}",
            training_backend="mlx-lm",
            training_method="qlora",
            data_dir=str((tmp_path / "data").resolve()),
            adapter_dir=str((tmp_path / "adapter").resolve()),
            training_log_path=str((tmp_path / "train.log").resolve()),
            metadata_path=str((tmp_path / "training-result.json").resolve()),
            command=("python", "-m", "mlx_lm.lora"),
            adapter_artifact=adapter_artifact,
        )

    monkeypatch.setattr(
        self_learning_cycle,
        "run_training_spec_with_mlx_lm",
        fake_run_training_spec_with_mlx_lm,
    )

    def fake_package_adapter_artifact_for_ollama(**kwargs):
        class _Packaged:
            ollama_model_name = kwargs["ollama_model_name"]
            modelfile_path = str((tmp_path / "Modelfile").resolve())
            metadata_path = str((tmp_path / "ollama-package.json").resolve())
            output_dir = str(tmp_path.resolve())
            created_at = "2026-05-19T10:05:00Z"
            adapter_artifact = fake_run_training_spec_with_mlx_lm(
                spec_key=spec_key,
                spec_version=spec_version,
                payload=TrainingSpecRunRequest(
                    adapter_key="cycle-adapter",
                    adapter_version="2026-05-19.1",
                    adapter_name="Cycle Adapter",
                    adapter_description="Fixture cycle adapter.",
                ),
            ).adapter_artifact

        return _Packaged()

    monkeypatch.setattr(
        self_learning_cycle,
        "package_adapter_artifact_for_ollama",
        fake_package_adapter_artifact_for_ollama,
    )

    result = self_learning_cycle.run_daily_self_learning_cycle(
        spec_key=spec_key,
        spec_version=spec_version,
        adapter_key="cycle-adapter",
        adapter_version="2026-05-19.1",
        adapter_name="Cycle Adapter",
        adapter_description="Fixture cycle adapter.",
        artifact_format="safetensors",
        comparison_report_file=str(comparison_path.resolve()),
        package_for_ollama=True,
        ollama_model_name="train-reply-adapter:cycle",
    )

    assert result.promotion_ready is True
    assert result.grader_suite_run is not None
    assert result.packaging is not None
    assert result.packaging["ollama_model_name"] == "train-reply-adapter:cycle"
    assert result.blocked_reasons == ()

    with SessionLocal() as db:
        delete_eval_dataset(db, dataset_key, dataset_version)


def test_training_spec_readiness_route(monkeypatch, tmp_path: Path) -> None:
    @dataclass(frozen=True)
    class FakeSpec:
        ref: str = "reply_sft@2026-05-19.1"
        base_model_source_kind: str = "huggingface"
        base_model_ref: str = "mlx-community/Llama-3.2-3B-Instruct-4bit"
        output_dir: str = str(tmp_path / "output")

    monkeypatch.setattr("train_api.main.get_training_spec", lambda *args, **kwargs: FakeSpec())
    monkeypatch.setattr(
        "train_api.main.check_training_lane_readiness",
        lambda **kwargs: HealthCheckResult(
            key="offline-training",
            status="pass",
            summary="ready",
            details={"training_spec_ref": "reply_sft@2026-05-19.1"},
            remediation=None,
        ),
    )

    result = get_training_spec_readiness("reply_sft", "2026-05-19.1", db=None)

    assert isinstance(result, TrainingReadinessRead)
    assert result.status == "pass"
    assert result.training_spec_ref == "reply_sft@2026-05-19.1"


def test_run_self_learning_cycle_route(monkeypatch) -> None:
    monkeypatch.setattr(
        "train_api.main.run_daily_self_learning_cycle",
        lambda **kwargs: self_learning_cycle.SelfLearningCycleResult(
            generated_at="2026-05-19T10:00:00Z",
            training_spec_ref="reply_sft@2026-05-19.1",
            health_report={"overall_status": "pass"},
            training_readiness={"status": "pass"},
            training_run={"training_spec_ref": "reply_sft@2026-05-19.1"},
            grader_suite_run={"summary": "passed"},
            packaging=None,
            promotion_ready=True,
            blocked_reasons=(),
        ),
    )

    result = run_self_learning_cycle_route(
        "reply_sft",
        "2026-05-19.1",
        SelfLearningCycleRequest(
            adapter_key="reply_adapter_candidate",
            adapter_version="2026-05-19.1",
            adapter_name="Reply Adapter Candidate",
            adapter_description="Fixture route cycle.",
            comparison_report_file="/tmp/comparison.json",
        ),
    )

    assert isinstance(result, SelfLearningCycleRead)
    assert result.promotion_ready is True
    assert result.training_spec_ref == "reply_sft@2026-05-19.1"


def test_training_spec_accepts_local_path_model_ref(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()

    spec = TrainingSpecWrite(
        key="local-model-spec",
        version="2026-05-18.1",
        name="Local Model Spec",
        description="Validates local-path base model refs.",
        dataset_key="dataset",
        dataset_version="2026-05-18.1",
        grader_suite_key="suite",
        grader_suite_version="2026-05-18.1",
        base_model_ref="llms/chat/gemma-3-270m-it-mlx-8bit",
        base_model_source_kind="local-path",
        template_ref="chatml://reply-v1",
        tokenizer_ref=None,
        training_backend="mlx-lm",
        training_stage="sft",
        training_method="qlora",
        expected_adapter_family="reply_adapter",
        output_dir=str(output_dir.resolve()),
        hyperparameters={},
        provenance={},
    )

    assert spec.base_model_source_kind == "local-path"


def test_training_spec_rejects_ollama_base_model_for_mlx_lm(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()

    try:
        TrainingSpecWrite(
            key="ollama-model-spec",
            version="2026-05-18.1",
            name="Ollama Model Spec",
            description="Rejects ollama refs for mlx-lm.",
            dataset_key="dataset",
            dataset_version="2026-05-18.1",
            grader_suite_key="suite",
            grader_suite_version="2026-05-18.1",
            base_model_ref="gemma3:4b",
            base_model_source_kind="ollama",
            template_ref="chatml://reply-v1",
            tokenizer_ref=None,
            training_backend="mlx-lm",
            training_stage="sft",
            training_method="qlora",
            expected_adapter_family="reply_adapter",
            output_dir=str(output_dir.resolve()),
            hyperparameters={},
            provenance={},
        )
    except ValueError as exc:
        assert "do not support ollama" in str(exc)
    else:
        raise AssertionError("Expected ollama base_model_source_kind to fail for mlx-lm.")
