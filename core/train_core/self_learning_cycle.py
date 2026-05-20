from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from train_core.fine_tuning import get_training_spec
from train_core.grader_suites import run_grader_suite
from train_core.health import build_doctor_report, check_training_lane_readiness
from train_core.mlx_lm_worker import run_training_spec_with_mlx_lm
from train_core.ollama_packaging import package_adapter_artifact_for_ollama
from train_core.schemas import GraderSuiteRunRequest, TrainingSpecRunRequest


class SelfLearningCycleError(ValueError):
    """Raised when one bounded self-learning cycle cannot be completed safely."""


@dataclass(frozen=True)
class SelfLearningCycleResult:
    generated_at: str
    training_spec_ref: str
    health_report: dict[str, object]
    training_readiness: dict[str, object]
    training_run: dict[str, object]
    grader_suite_run: dict[str, object] | None
    packaging: dict[str, object] | None
    promotion_ready: bool
    blocked_reasons: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "generated_at": self.generated_at,
            "training_spec_ref": self.training_spec_ref,
            "health_report": self.health_report,
            "training_readiness": self.training_readiness,
            "training_run": self.training_run,
            "grader_suite_run": self.grader_suite_run,
            "packaging": self.packaging,
            "promotion_ready": self.promotion_ready,
            "blocked_reasons": list(self.blocked_reasons),
        }


def run_daily_self_learning_cycle(
    *,
    spec_key: str,
    spec_version: str,
    adapter_key: str,
    adapter_version: str,
    adapter_name: str,
    adapter_description: str,
    artifact_format: str,
    comparison_report_file: str | None = None,
    evaluator_artifact_files: tuple[dict[str, str], ...] = (),
    grader_output_path: str | None = None,
    package_for_ollama: bool = False,
    ollama_model_name: str | None = None,
    package_output_dir: str | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    system_prompt: str | None = None,
    api_base_url: str | None = None,
    trinity_root: str | None = None,
    provenance: dict[str, object] | None = None,
) -> SelfLearningCycleResult:
    spec = get_training_spec(spec_key, spec_version)
    if spec is None:
        raise SelfLearningCycleError(
            f"Training spec '{spec_key}' version '{spec_version}' was not found."
        )

    health_report = build_doctor_report(
        workflow="training",
        api_base_url=api_base_url,
        trinity_root=trinity_root,
    )
    if not health_report.ok:
        raise SelfLearningCycleError("Doctor checks failed for the training workflow.")

    readiness = check_training_lane_readiness(required=True, spec=spec)
    if readiness.status != "pass":
        raise SelfLearningCycleError(readiness.summary)

    training_run = run_training_spec_with_mlx_lm(
        spec_key=spec_key,
        spec_version=spec_version,
        payload=TrainingSpecRunRequest(
            adapter_key=adapter_key,
            adapter_version=adapter_version,
            adapter_name=adapter_name,
            adapter_description=adapter_description,
            artifact_format=artifact_format,
            provenance=dict(provenance or {}),
        ),
    )

    grader_suite_run = None
    packaging = None
    blocked_reasons: list[str] = []
    promotion_ready = False

    if comparison_report_file is None:
        blocked_reasons.append(
            "No comparison report was provided, so grader-suite evaluation and promotion remain blocked."
        )
    else:
        comparison_path = Path(comparison_report_file).expanduser().resolve()
        grader_suite_run = run_grader_suite(
            dataset_key=spec.dataset_key,
            dataset_version=spec.dataset_version,
            key=spec.grader_suite_key,
            version=spec.grader_suite_version,
            payload=GraderSuiteRunRequest(
                proposal_family=spec.expected_adapter_family,
                proposal_artifact_version=adapter_version,
                comparison_report_file=str(comparison_path),
                evaluator_artifact_files=evaluator_artifact_files,
                output_path=str(Path(grader_output_path).expanduser().resolve())
                if grader_output_path is not None
                else None,
            ),
        )
        failing_graders = tuple(
            str(item.get("grader_key") or "?")
            for item in grader_suite_run.grader_results
            if item.get("passed") is not True
        )
        if failing_graders:
            blocked_reasons.append(
                "Grader-suite evaluation did not fully pass: " + ", ".join(failing_graders)
            )
        else:
            promotion_ready = True

    if package_for_ollama:
        if not ollama_model_name:
            raise SelfLearningCycleError(
                "ollama_model_name is required when package_for_ollama is enabled."
            )
        if not promotion_ready:
            blocked_reasons.append(
                "Ollama packaging was requested, but promotion is blocked until grader-suite evidence passes."
            )
        else:
            packaged = package_adapter_artifact_for_ollama(
                artifact_key=adapter_key,
                artifact_version=adapter_version,
                ollama_model_name=ollama_model_name,
                output_dir=package_output_dir,
                temperature=temperature,
                top_p=top_p,
                system_prompt=system_prompt,
            )
            packaging = {
                "ollama_model_name": packaged.ollama_model_name,
                "modelfile_path": packaged.modelfile_path,
                "metadata_path": packaged.metadata_path,
                "output_dir": packaged.output_dir,
                "created_at": packaged.created_at,
                "adapter_artifact": packaged.adapter_artifact.model_dump(mode="json"),
            }

    return SelfLearningCycleResult(
        generated_at=datetime.now(UTC).isoformat(),
        training_spec_ref=spec.ref,
        health_report=health_report.to_payload(),
        training_readiness={
            "status": readiness.status,
            "summary": readiness.summary,
            "details": readiness.details,
            "remediation": readiness.remediation,
        },
        training_run=training_run.model_dump(mode="json"),
        grader_suite_run=None if grader_suite_run is None else grader_suite_run.model_dump(mode="json"),
        packaging=packaging,
        promotion_ready=promotion_ready and packaging is not None if package_for_ollama else promotion_ready,
        blocked_reasons=tuple(blocked_reasons),
    )
