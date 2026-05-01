from __future__ import annotations

import json
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "artifacts"
TRAIN_PATH = DATA_DIR / "train.json"
VAL_PATH = DATA_DIR / "val.json"
META_PATH = DATA_DIR / "meta.json"


DATASET = [
    {"text": "I was charged twice for my monthly plan and need a refund.", "label": "billing"},
    {"text": "My invoice total looks wrong after I upgraded seats yesterday.", "label": "billing"},
    {"text": "Can you send the receipt for the payment that cleared this morning?", "label": "billing"},
    {"text": "The card on file failed and now my subscription is paused.", "label": "billing"},
    {"text": "The app crashes every time I upload a PDF from Safari.", "label": "technical"},
    {"text": "After the latest update, our dashboard takes forever to load.", "label": "technical"},
    {"text": "The export button is stuck on spinning and never finishes.", "label": "technical"},
    {"text": "I keep getting a server error when I try to save workflow changes.", "label": "technical"},
    {"text": "I cannot reset my password because the email never arrives.", "label": "account"},
    {"text": "Please remove a former teammate from our workspace access list.", "label": "account"},
    {"text": "How do I change the owner of this organization to another admin?", "label": "account"},
    {"text": "Two-factor login is locking me out after I replaced my phone.", "label": "account"},
    {"text": "Our card expired and the renewal payment did not go through.", "label": "billing"},
    {"text": "The browser tab freezes whenever I open analytics for April.", "label": "technical"},
    {"text": "I need to rename a user profile and update the login email.", "label": "account"},
    {"text": "Please explain why this statement includes an extra prorated charge.", "label": "billing"},
    {"text": "Uploading images fails with an unknown network error.", "label": "technical"},
    {"text": "Can you unlock my account after too many failed sign-in attempts?", "label": "account"},
]


def build_splits() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    train_items: list[dict[str, str]] = []
    val_items: list[dict[str, str]] = []
    for index, item in enumerate(DATASET):
        if index % 4 == 0:
            val_items.append(item)
        else:
            train_items.append(item)
    return train_items, val_items


def ensure_prepared() -> dict[str, int]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    train_items, val_items = build_splits()
    TRAIN_PATH.write_text(json.dumps(train_items, indent=2), encoding="utf-8")
    VAL_PATH.write_text(json.dumps(val_items, indent=2), encoding="utf-8")
    metadata = {
        "train_examples": len(train_items),
        "val_examples": len(val_items),
        "labels": 3,
    }
    META_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    print(json.dumps(ensure_prepared()))


if __name__ == "__main__":
    main()
