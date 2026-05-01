from __future__ import annotations

import argparse
import json

from prepare import TRAIN_PATH, VAL_PATH, ensure_prepared
from train import macro_f1, train_model


def run_benchmark() -> dict[str, object]:
    ensure_prepared()
    train_examples = json.loads(TRAIN_PATH.read_text(encoding="utf-8"))
    val_examples = json.loads(VAL_PATH.read_text(encoding="utf-8"))

    model = train_model(train_examples)
    metric_value = round(macro_f1(model, val_examples), 6)

    return {
        "status": "succeeded",
        "metric_value": metric_value,
        "result_summary": (
            "Helpdesk intent benchmark completed with a deterministic macro-F1 score on the "
            "validation split."
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
