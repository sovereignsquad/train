from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass


# Mutable benchmark configuration. This is the only file the autonomous loop
# should tune for the helpdesk reference project.
LOWERCASE = True
STRIP_PUNCTUATION = True
MIN_TOKEN_LENGTH = 3
KEYWORD_BOOST = 1.5
PRIOR_BOOST = 0.35
FALLBACK_LABEL = "technical"

LABEL_KEYWORDS = {
    "billing": {
        "charge": 1.4,
        "charged": 1.7,
        "refund": 2.0,
        "invoice": 1.8,
        "payment": 1.6,
        "receipt": 1.4,
        "subscription": 1.0,
        "renewal": 1.3,
        "card": 1.1,
    },
    "technical": {
        "crash": 1.9,
        "error": 1.8,
        "upload": 1.4,
        "export": 1.3,
        "dashboard": 1.1,
        "load": 1.2,
        "freezes": 1.8,
        "server": 1.6,
        "network": 1.2,
    },
    "account": {
        "password": 1.8,
        "login": 1.6,
        "email": 1.4,
        "owner": 1.3,
        "admin": 1.1,
        "workspace": 1.2,
        "profile": 1.2,
        "unlock": 1.7,
        "account": 1.5,
    },
}


def preprocess_text(text: str) -> list[str]:
    if LOWERCASE:
        text = text.lower()
    if STRIP_PUNCTUATION:
        text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [token for token in text.split() if len(token) >= MIN_TOKEN_LENGTH]


@dataclass
class HelpdeskClassifier:
    label_token_scores: dict[str, Counter[str]]
    label_priors: dict[str, float]


def train_model(examples: list[dict[str, str]]) -> HelpdeskClassifier:
    label_token_scores: dict[str, Counter[str]] = defaultdict(Counter)
    label_counts: Counter[str] = Counter()

    for example in examples:
        label = example["label"]
        label_counts[label] += 1
        for token in preprocess_text(example["text"]):
            label_token_scores[label][token] += 1.0

    for label, keywords in LABEL_KEYWORDS.items():
        for token, weight in keywords.items():
            label_token_scores[label][token] += weight * KEYWORD_BOOST

    total = sum(label_counts.values()) or 1
    label_priors = {
        label: (count / total) * PRIOR_BOOST for label, count in label_counts.items()
    }

    return HelpdeskClassifier(label_token_scores=dict(label_token_scores), label_priors=label_priors)


def predict_label(model: HelpdeskClassifier, text: str) -> str:
    tokens = preprocess_text(text)
    best_label = FALLBACK_LABEL
    best_score = float("-inf")

    for label, scores in model.label_token_scores.items():
        score = model.label_priors.get(label, 0.0)
        for token in tokens:
            score += scores.get(token, 0.0)
        if score > best_score:
            best_label = label
            best_score = score

    return best_label


def macro_f1(model: HelpdeskClassifier, examples: list[dict[str, str]]) -> float:
    labels = sorted(model.label_token_scores)
    if not labels:
        return 0.0

    tp: Counter[str] = Counter()
    fp: Counter[str] = Counter()
    fn: Counter[str] = Counter()

    for example in examples:
        actual = example["label"]
        predicted = predict_label(model, example["text"])
        if predicted == actual:
            tp[actual] += 1
        else:
            fp[predicted] += 1
            fn[actual] += 1

    f1_scores: list[float] = []
    for label in labels:
        precision_denom = tp[label] + fp[label]
        recall_denom = tp[label] + fn[label]
        precision = tp[label] / precision_denom if precision_denom else 0.0
        recall = tp[label] / recall_denom if recall_denom else 0.0
        if precision + recall == 0:
            f1_scores.append(0.0)
            continue
        f1_scores.append((2 * precision * recall) / (precision + recall))

    return sum(f1_scores) / len(f1_scores)
