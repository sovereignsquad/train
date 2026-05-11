from __future__ import annotations

import argparse
import json
import sys

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
    propose_parser.add_argument("--bundle-file", action="append", required=True)
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
    propose_spot_parser.add_argument("--bundle-file", action="append", required=True)
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

    args = parser.parse_args(argv)

    if args.command == "propose-reply-policy":
        result = propose_reply_policy_from_bundle_files(
            learner_kind=str(args.learner_kind),
            bundle_files=list(args.bundle_file),
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


if __name__ == "__main__":
    raise SystemExit(main())
