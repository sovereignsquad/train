from __future__ import annotations

import argparse
import json
import os
import sys

from train_core.fine_tuning import get_training_spec
from train_core.grader_suites import run_grader_suite
from train_core.health import build_doctor_report, check_training_lane_readiness, render_health_report
from train_core.mlx_lm_worker import run_training_spec_with_mlx_lm
from train_core.ollama_packaging import package_adapter_artifact_for_ollama
from train_core.schemas import GraderSuiteRunRequest, TrainingSpecRunRequest
from train_core.self_learning_cycle import run_daily_self_learning_cycle
from train_core.trinity_reply_policy_service import propose_reply_policy_from_bundle_files
from train_core.trinity_skeptical_eval import build_skeptical_eval_report
from train_core.trinity_spot_policy_service import propose_spot_review_policy_from_bundle_files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="train")
    subparsers = parser.add_subparsers(dest="command", required=True)

    propose_parser = subparsers.add_parser(
        "propose-reply-policy",
        help="Generate one bounded reply behavior policy proposal from Trinity training bundles.",
    )
    propose_parser.add_argument("--learner-kind", required=True)
    propose_parser.add_argument("--bundle-file", action="append", default=[])
    propose_parser.add_argument("--eval-dataset-key")
    propose_parser.add_argument("--eval-dataset-version")
    propose_parser.add_argument("--eval-dataset-slice-key")
    propose_parser.add_argument("--eval-dataset-slice-version")
    propose_parser.add_argument("--baseline-policy-file")
    propose_parser.add_argument("--incumbent-policy-file")
    propose_parser.add_argument("--proposal-output-path")
    propose_parser.add_argument("--eval-output-path")
    propose_parser.add_argument("--comparison-output-path")
    propose_parser.add_argument(
        "--output-format",
        choices=("json", "summary", "matrix"),
        default="json",
    )

    propose_spot_parser = subparsers.add_parser(
        "propose-spot-review-policy",
        help="Generate one bounded Spot review policy proposal from Trinity training bundles.",
    )
    propose_spot_parser.add_argument("--learner-kind", required=True)
    propose_spot_parser.add_argument("--bundle-file", action="append", default=[])
    propose_spot_parser.add_argument("--eval-dataset-key")
    propose_spot_parser.add_argument("--eval-dataset-version")
    propose_spot_parser.add_argument("--eval-dataset-slice-key")
    propose_spot_parser.add_argument("--eval-dataset-slice-version")
    propose_spot_parser.add_argument("--proposal-output-path")
    propose_spot_parser.add_argument("--eval-output-path")
    propose_spot_parser.add_argument("--comparison-output-path")
    propose_spot_parser.add_argument(
        "--output-format",
        choices=("json", "summary", "matrix"),
        default="json",
    )

    skeptical_eval_parser = subparsers.add_parser(
        "build-skeptical-eval-report",
        help="Generate one skeptical review artifact from a bounded proposal and comparison report.",
    )
    skeptical_eval_parser.add_argument("--component-key", required=True)
    skeptical_eval_parser.add_argument("--artifact-family", required=True)
    skeptical_eval_parser.add_argument("--proposal-artifact-version", required=True)
    skeptical_eval_parser.add_argument("--proposal-ref", required=True)
    skeptical_eval_parser.add_argument("--comparison-report-file", required=True)
    skeptical_eval_parser.add_argument("--review-scope-kind", required=True)
    skeptical_eval_parser.add_argument("--review-scope-value")
    skeptical_eval_parser.add_argument("--minimum-sample-count", type=int, default=5)
    skeptical_eval_parser.add_argument("--minimum-improvement-delta", type=float, default=0.02)
    skeptical_eval_parser.add_argument("--hidden-confound", action="append", default=[])
    skeptical_eval_parser.add_argument("--overfitting-risk", action="append", default=[])
    skeptical_eval_parser.add_argument("--weak-assumption", action="append", default=[])
    skeptical_eval_parser.add_argument("--disconfirming-signal", action="append", default=[])
    skeptical_eval_parser.add_argument("--skeptical-eval-output-path")
    skeptical_eval_parser.add_argument(
        "--output-format",
        choices=("json", "summary"),
        default="json",
    )

    grader_suite_parser = subparsers.add_parser(
        "run-grader-suite",
        help="Run one persistent grader suite against a comparison artifact.",
    )
    grader_suite_parser.add_argument("--dataset-key", required=True)
    grader_suite_parser.add_argument("--dataset-version", required=True)
    grader_suite_parser.add_argument("--suite-key", required=True)
    grader_suite_parser.add_argument("--suite-version", required=True)
    grader_suite_parser.add_argument("--proposal-family", required=True)
    grader_suite_parser.add_argument("--proposal-artifact-version", required=True)
    grader_suite_parser.add_argument("--comparison-report-file", required=True)
    grader_suite_parser.add_argument(
        "--evaluator-artifact-file",
        action="append",
        default=[],
        help="Pair in the form grader_key=/absolute/path/to/artifact.json",
    )
    grader_suite_parser.add_argument("--output-path")
    grader_suite_parser.add_argument(
        "--output-format",
        choices=("json", "summary"),
        default="json",
    )

    training_parser = subparsers.add_parser(
        "run-training-spec",
        help="Run one bounded mlx-lm training job from a persisted training spec.",
    )
    training_parser.add_argument("--spec-key", required=True)
    training_parser.add_argument("--spec-version", required=True)
    training_parser.add_argument("--adapter-key", required=True)
    training_parser.add_argument("--adapter-version", required=True)
    training_parser.add_argument("--adapter-name", required=True)
    training_parser.add_argument("--adapter-description", required=True)
    training_parser.add_argument(
        "--artifact-format",
        default="safetensors",
        choices=("safetensors",),
    )
    training_parser.add_argument("--provenance-file")
    training_parser.add_argument(
        "--output-format",
        choices=("json", "summary"),
        default="json",
    )

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Report the readiness of the current train integration surface.",
    )
    doctor_parser.add_argument(
        "--workflow",
        choices=("default", "training"),
        default="default",
    )
    doctor_parser.add_argument("--api-base-url")
    doctor_parser.add_argument("--trinity-root")
    doctor_parser.add_argument(
        "--output-format",
        choices=("json", "summary"),
        default="summary",
    )

    training_readiness_parser = subparsers.add_parser(
        "check-training-readiness",
        help="Check whether one persisted training spec is runnable in the current local environment.",
    )
    training_readiness_parser.add_argument("--spec-key", required=True)
    training_readiness_parser.add_argument("--spec-version", required=True)
    training_readiness_parser.add_argument(
        "--output-format",
        choices=("json", "summary"),
        default="summary",
    )

    package_parser = subparsers.add_parser(
        "package-adapter-artifact-for-ollama",
        help="Generate a deterministic local Ollama package for one adapter artifact.",
    )
    package_parser.add_argument("--artifact-key", required=True)
    package_parser.add_argument("--artifact-version", required=True)
    package_parser.add_argument("--ollama-model-name", required=True)
    package_parser.add_argument("--output-dir")
    package_parser.add_argument("--temperature", type=float)
    package_parser.add_argument("--top-p", type=float)
    package_parser.add_argument("--system-prompt")
    package_parser.add_argument(
        "--output-format",
        choices=("json", "summary"),
        default="json",
    )

    self_learning_parser = subparsers.add_parser(
        "run-daily-self-learning-cycle",
        help="Run one bounded offline self-learning cycle from doctor checks through optional packaging.",
    )
    self_learning_parser.add_argument("--spec-key", required=True)
    self_learning_parser.add_argument("--spec-version", required=True)
    self_learning_parser.add_argument("--adapter-key", required=True)
    self_learning_parser.add_argument("--adapter-version", required=True)
    self_learning_parser.add_argument("--adapter-name", required=True)
    self_learning_parser.add_argument("--adapter-description", required=True)
    self_learning_parser.add_argument(
        "--artifact-format",
        default="safetensors",
        choices=("safetensors",),
    )
    self_learning_parser.add_argument("--comparison-report-file")
    self_learning_parser.add_argument(
        "--evaluator-artifact-file",
        action="append",
        default=[],
        help="Pair in the form grader_key=/absolute/path/to/artifact.json",
    )
    self_learning_parser.add_argument("--grader-output-path")
    self_learning_parser.add_argument("--package-for-ollama", action="store_true")
    self_learning_parser.add_argument("--ollama-model-name")
    self_learning_parser.add_argument("--package-output-dir")
    self_learning_parser.add_argument("--temperature", type=float)
    self_learning_parser.add_argument("--top-p", type=float)
    self_learning_parser.add_argument("--system-prompt")
    self_learning_parser.add_argument("--api-base-url")
    self_learning_parser.add_argument("--trinity-root")
    self_learning_parser.add_argument("--provenance-file")
    self_learning_parser.add_argument(
        "--output-format",
        choices=("json", "summary"),
        default="json",
    )

    args = parser.parse_args(argv)

    if args.command == "propose-reply-policy":
        result = propose_reply_policy_from_bundle_files(
            learner_kind=str(args.learner_kind),
            bundle_files=list(args.bundle_file),
            eval_dataset_key=args.eval_dataset_key,
            eval_dataset_version=args.eval_dataset_version,
            eval_dataset_slice_key=args.eval_dataset_slice_key,
            eval_dataset_slice_version=args.eval_dataset_slice_version,
            baseline_policy_file=args.baseline_policy_file,
            incumbent_policy_file=args.incumbent_policy_file,
            proposal_output_path=args.proposal_output_path,
            eval_output_path=args.eval_output_path,
            comparison_output_path=args.comparison_output_path,
        )
        if args.output_format == "json":
            json.dump(result.model_dump(mode="json"), sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
        elif args.output_format == "summary":
            _write_summary(result)
        else:
            _write_matrix(result)
        return 0

    if args.command == "propose-spot-review-policy":
        result = propose_spot_review_policy_from_bundle_files(
            learner_kind=str(args.learner_kind),
            bundle_files=list(args.bundle_file),
            eval_dataset_key=args.eval_dataset_key,
            eval_dataset_version=args.eval_dataset_version,
            eval_dataset_slice_key=args.eval_dataset_slice_key,
            eval_dataset_slice_version=args.eval_dataset_slice_version,
            proposal_output_path=args.proposal_output_path,
            eval_output_path=args.eval_output_path,
            comparison_output_path=args.comparison_output_path,
        )
        if args.output_format == "json":
            json.dump(result.model_dump(mode="json"), sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
        elif args.output_format == "summary":
            _write_summary(result)
        else:
            _write_matrix(result)
        return 0

    if args.command == "build-skeptical-eval-report":
        result = build_skeptical_eval_report(
            component_key=str(args.component_key),
            artifact_family=str(args.artifact_family),
            proposal_artifact_version=str(args.proposal_artifact_version),
            proposal_ref=str(args.proposal_ref),
            comparison_report_file=str(args.comparison_report_file),
            review_scope_kind=str(args.review_scope_kind),
            review_scope_value=args.review_scope_value,
            minimum_sample_count=int(args.minimum_sample_count),
            minimum_improvement_delta=float(args.minimum_improvement_delta),
            hidden_confounds=tuple(str(item) for item in args.hidden_confound),
            overfitting_risks=tuple(str(item) for item in args.overfitting_risk),
            weak_assumptions=tuple(str(item) for item in args.weak_assumption),
            disconfirming_signals=tuple(str(item) for item in args.disconfirming_signal),
            skeptical_eval_output_path=args.skeptical_eval_output_path,
        )
        if args.output_format == "json":
            json.dump(result.model_dump(mode="json"), sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
        else:
            _write_skeptical_summary(result)
        return 0

    if args.command == "run-grader-suite":
        result = run_grader_suite(
            dataset_key=str(args.dataset_key),
            dataset_version=str(args.dataset_version),
            key=str(args.suite_key),
            version=str(args.suite_version),
            payload=GraderSuiteRunRequest(
                proposal_family=str(args.proposal_family),
                proposal_artifact_version=str(args.proposal_artifact_version),
                comparison_report_file=str(args.comparison_report_file),
                evaluator_artifact_files=tuple(_parse_evaluator_artifact_files(args.evaluator_artifact_file)),
                output_path=args.output_path,
            ),
        )
        if args.output_format == "json":
            json.dump(result.model_dump(mode="json"), sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
        else:
            _write_grader_suite_summary(result)
        return 0

    if args.command == "run-training-spec":
        result = run_training_spec_with_mlx_lm(
            spec_key=str(args.spec_key),
            spec_version=str(args.spec_version),
            payload=TrainingSpecRunRequest(
                adapter_key=str(args.adapter_key),
                adapter_version=str(args.adapter_version),
                adapter_name=str(args.adapter_name),
                adapter_description=str(args.adapter_description),
                artifact_format=str(args.artifact_format),
                provenance=_load_json_file(args.provenance_file),
            ),
        )
        if args.output_format == "json":
            json.dump(result.model_dump(mode="json"), sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
        else:
            _write_training_summary(result)
        return 0

    if args.command == "doctor":
        report = build_doctor_report(
            workflow=str(args.workflow),
            api_base_url=args.api_base_url,
            trinity_root=args.trinity_root,
        )
        if args.output_format == "json":
            json.dump(report.to_payload(), sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
        else:
            sys.stdout.write(f"{render_health_report(report)}\n")
        return 0 if report.ok else 1

    if args.command == "check-training-readiness":
        spec = get_training_spec(str(args.spec_key), str(args.spec_version))
        if spec is None:
            raise ValueError(
                f"Training spec '{args.spec_key}' version '{args.spec_version}' was not found."
            )
        check = check_training_lane_readiness(required=True, spec=spec)
        if args.output_format == "json":
            json.dump(
                {
                    "training_spec_ref": spec.ref,
                    "status": check.status,
                    "summary": check.summary,
                    "details": check.details,
                    "remediation": check.remediation,
                },
                sys.stdout,
                indent=2,
                sort_keys=True,
            )
            sys.stdout.write("\n")
        else:
            sys.stdout.write(f"training_spec_ref: {spec.ref}\n")
            sys.stdout.write(f"status: {check.status}\n")
            sys.stdout.write(f"summary: {check.summary}\n")
            for problem in check.details.get("problems", ()):
                sys.stdout.write(f"problem: {problem}\n")
            if check.remediation:
                sys.stdout.write(f"remediation: {check.remediation}\n")
        return 0 if check.status == "pass" else 1

    if args.command == "package-adapter-artifact-for-ollama":
        result = package_adapter_artifact_for_ollama(
            artifact_key=str(args.artifact_key),
            artifact_version=str(args.artifact_version),
            ollama_model_name=str(args.ollama_model_name),
            output_dir=args.output_dir,
            temperature=args.temperature,
            top_p=args.top_p,
            system_prompt=args.system_prompt,
        )
        payload = {
            "ollama_model_name": result.ollama_model_name,
            "modelfile_path": result.modelfile_path,
            "metadata_path": result.metadata_path,
            "output_dir": result.output_dir,
            "created_at": result.created_at,
            "adapter_artifact": result.adapter_artifact.model_dump(mode="json"),
        }
        if args.output_format == "json":
            json.dump(payload, sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
        else:
            sys.stdout.write(f"ollama_model_name: {result.ollama_model_name}\n")
            sys.stdout.write(f"modelfile_path: {result.modelfile_path}\n")
            sys.stdout.write(f"metadata_path: {result.metadata_path}\n")
            sys.stdout.write(f"adapter_artifact_ref: {result.adapter_artifact.ref}\n")
        return 0

    if args.command == "run-daily-self-learning-cycle":
        result = run_daily_self_learning_cycle(
            spec_key=str(args.spec_key),
            spec_version=str(args.spec_version),
            adapter_key=str(args.adapter_key),
            adapter_version=str(args.adapter_version),
            adapter_name=str(args.adapter_name),
            adapter_description=str(args.adapter_description),
            artifact_format=str(args.artifact_format),
            comparison_report_file=args.comparison_report_file,
            evaluator_artifact_files=tuple(_parse_evaluator_artifact_files(args.evaluator_artifact_file)),
            grader_output_path=args.grader_output_path,
            package_for_ollama=bool(args.package_for_ollama),
            ollama_model_name=args.ollama_model_name,
            package_output_dir=args.package_output_dir,
            temperature=args.temperature,
            top_p=args.top_p,
            system_prompt=args.system_prompt,
            api_base_url=args.api_base_url,
            trinity_root=args.trinity_root,
            provenance=_load_json_file(args.provenance_file),
        )
        if args.output_format == "json":
            json.dump(result.to_payload(), sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
        else:
            sys.stdout.write(f"training_spec_ref: {result.training_spec_ref}\n")
            sys.stdout.write(f"promotion_ready: {str(result.promotion_ready).lower()}\n")
            if result.grader_suite_run is not None:
                sys.stdout.write(
                    f"grader_suite_summary: {result.grader_suite_run.get('summary', '')}\n"
                )
            if result.packaging is not None:
                sys.stdout.write(
                    f"packaged_ollama_model: {result.packaging.get('ollama_model_name', '')}\n"
                )
            for reason in result.blocked_reasons:
                sys.stdout.write(f"blocked: {reason}\n")
        return 0 if result.promotion_ready else 1

    raise AssertionError("Unhandled command.")


def _write_summary(result) -> None:
    comparison = result.comparison_report or {}
    summary = str(comparison.get("summary") or "")
    if summary:
        sys.stdout.write(f"{summary}\n")
    rows = comparison.get("rows") or []
    for row in rows:
        label = str(row.get("label") or "?")
        score = row.get("score")
        status = str(row.get("status") or "")
        rendered_score = "-" if score is None else f"{float(score):.6f}"
        sys.stdout.write(f"{label}: {rendered_score} [{status}]\n")


def _write_matrix(result) -> None:
    comparison = result.comparison_report or {}
    table = str(comparison.get("table_markdown") or "").strip()
    if table:
        sys.stdout.write(f"{table}\n")
    else:
        _write_summary(result)


def _write_skeptical_summary(result) -> None:
    report = result.skeptical_eval_report or {}
    sys.stdout.write(f"{report.get('primary_decision_summary', '')}\n")
    sys.stdout.write(
        f"review_outcome: {report.get('review_outcome', '?')} "
        f"[{report.get('promotion_readiness', '?')}]\n"
    )
    for item in report.get("rejection_evidence") or []:
        reason = str(item.get("reason_code") or "?")
        severity = str(item.get("severity") or "?")
        blocking = "blocking" if item.get("blocking") else "advisory"
        sys.stdout.write(f"{reason}: {severity} [{blocking}]\n")


def _write_grader_suite_summary(result) -> None:
    sys.stdout.write(f"{result.summary}\n")
    for item in result.grader_results:
        status = str(item.get("status") or "?")
        score = item.get("score")
        rendered_score = "-" if score is None else f"{float(score):.6f}"
        sys.stdout.write(f"{item.get('grader_key', '?')}: {rendered_score} [{status}]\n")
    for item in result.disagreements:
        sys.stdout.write(f"disagreement: {item.get('summary', '')}\n")


def _write_training_summary(result) -> None:
    sys.stdout.write(
        f"Ran {result.training_backend} training for {result.training_spec_ref} "
        f"using {result.training_method}.\n"
    )
    sys.stdout.write(f"data_dir: {result.data_dir}\n")
    sys.stdout.write(f"adapter_dir: {result.adapter_dir}\n")
    sys.stdout.write(f"artifact: {result.adapter_artifact.ref} -> {result.adapter_artifact.artifact_path}\n")


def _parse_evaluator_artifact_files(values: list[str]) -> list[dict[str, str]]:
    parsed: list[dict[str, str]] = []
    for value in values:
        grader_key, separator, path = str(value).partition("=")
        if not separator or not grader_key.strip() or not path.strip():
            raise ValueError("evaluator artifact files must use grader_key=/absolute/path syntax")
        parsed.append({"grader_key": grader_key.strip(), "path": path.strip()})
    return parsed


def _load_json_file(path: str | None) -> dict[str, object]:
    if path is None:
        return {}
    if not os.path.isabs(path):
        raise ValueError("provenance-file must be absolute when provided")
    return json.loads(open(path, encoding="utf-8").read())


if __name__ == "__main__":
    raise SystemExit(main())
