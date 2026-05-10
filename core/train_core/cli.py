from __future__ import annotations

import argparse
import json
import sys

from train_core.trinity_reply_policy_service import propose_reply_policy_from_bundle_files
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


if __name__ == "__main__":
    raise SystemExit(main())
