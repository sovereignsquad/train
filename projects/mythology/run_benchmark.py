from __future__ import annotations

import argparse
import json
from pathlib import Path

from prepare import TRAIN_PATH, VAL_PATH, ensure_prepared
from train import bits_per_byte, train_model


def run_benchmark() -> dict[str, object]:
    ensure_prepared()
    train_text = TRAIN_PATH.read_text(encoding="utf-8")
    val_text = VAL_PATH.read_text(encoding="utf-8")

    model = train_model(train_text)
    metric_value = round(bits_per_byte(model, val_text), 6)

    return {
        "status": "succeeded",
        "metric_value": metric_value,
        "result_summary": (
            "Mythology benchmark completed with a real local character n-gram language "
            "model score on the validation set."
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
