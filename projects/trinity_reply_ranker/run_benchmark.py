from __future__ import annotations

import argparse
import json

from prepare import ensure_prepared, load_fixture
from train import evaluate_trace


def run_benchmark() -> dict[str, object]:
    ensure_prepared()
    fixture = load_fixture()
    metric_value = evaluate_trace(fixture["trace"])  # type: ignore[index]
    return {
        "status": "succeeded",
        "metric_value": metric_value,
        "result_summary": "Trinity reply trace replay scaffold completed against one bounded export fixture.",
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
