import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget-seconds", type=int, required=True)
    parser.add_argument("--run-id", type=int, required=True)
    args = parser.parse_args()

    # Placeholder benchmark result. This exists to prove the execution contract end to end.
    metric_value = round(max(0.1, 2.0 - min(args.budget_seconds, 300) / 1000), 6)

    payload = {
        "status": "succeeded",
        "metric_value": metric_value,
        "result_summary": (
            "Placeholder mythology benchmark completed successfully with a machine-readable "
            "metric payload."
        ),
        "error_message": None,
    }
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
