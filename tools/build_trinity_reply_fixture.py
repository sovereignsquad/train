from __future__ import annotations

import argparse

from train_core.trinity_reply_fixture_builder import write_fixture


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", required=True, help="Path to one {trinity} {reply} trace export JSON file.")
    parser.add_argument("--output", required=True, help="Where to write the generated fixture JSON.")
    parser.add_argument(
        "--shadow-log",
        default=None,
        help="Optional {reply} trinity-shadow comparison JSONL file to merge into the fixture.",
    )
    args = parser.parse_args()

    write_fixture(
        args.output,
        trace_path=args.trace,
        comparison_log_path=args.shadow_log,
    )


if __name__ == "__main__":
    main()
