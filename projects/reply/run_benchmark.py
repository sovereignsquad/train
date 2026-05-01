from __future__ import annotations

import argparse
import json

from prepare import ensure_prepared, load_examples
from train import draft_reply, score_reply


def run_benchmark() -> dict[str, object]:
    ensure_prepared()
    examples = load_examples()
    scores = [
        score_reply(draft_reply(example), example["gold_reply"])
        for example in examples
    ]
    metric_value = round(sum(scores) / len(scores), 6)

    return {
        "status": "succeeded",
        "metric_value": metric_value,
        "result_summary": (
            "Reply draft benchmark completed against the local starter fixture or local-only reply data."
        ),
        "error_message": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget-seconds", type=int, required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.parse_args()
    print(json.dumps(run_benchmark()))


if __name__ == "__main__":
    main()
