from __future__ import annotations

import argparse
import json
import sys

from train_core.trinity_reply_policy_service import propose_reply_policy_from_bundle_files


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
        json.dump(result.model_dump(mode="json"), sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    raise AssertionError("Unhandled command.")


if __name__ == "__main__":
    raise SystemExit(main())
