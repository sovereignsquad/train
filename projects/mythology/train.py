from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass


# Mutable benchmark configuration. This is the only file the autonomous loop
# should tune for the mythology reference project.
NGRAM_ORDER = 3
ADD_K_SMOOTHING = 0.6
LOWERCASE = True
NORMALIZE_WHITESPACE = True
START_TOKEN = "~"


def preprocess_text(text: str) -> str:
    if LOWERCASE:
        text = text.lower()
    if NORMALIZE_WHITESPACE:
        text = " ".join(text.split())
    return text


@dataclass
class CharNgramModel:
    order: int
    alphabet: list[str]
    context_counts: dict[str, Counter[str]]
    total_counts: dict[str, int]
    add_k: float


def train_model(text: str) -> CharNgramModel:
    processed = preprocess_text(text)
    order = max(1, NGRAM_ORDER)
    padded = (START_TOKEN * (order - 1)) + processed
    alphabet = sorted(set(processed) | {START_TOKEN})

    context_counts: dict[str, Counter[str]] = defaultdict(Counter)
    total_counts: dict[str, int] = defaultdict(int)

    for index in range(order - 1, len(padded)):
        context = padded[index - order + 1 : index]
        target = padded[index]
        context_counts[context][target] += 1
        total_counts[context] += 1

    return CharNgramModel(
        order=order,
        alphabet=alphabet,
        context_counts=dict(context_counts),
        total_counts=dict(total_counts),
        add_k=ADD_K_SMOOTHING,
    )


def bits_per_byte(model: CharNgramModel, text: str) -> float:
    processed = preprocess_text(text)
    if not processed:
        return 0.0

    padded = (START_TOKEN * (model.order - 1)) + processed
    total_log_prob = 0.0
    alphabet_size = len(model.alphabet)

    for index in range(model.order - 1, len(padded)):
        context = padded[index - model.order + 1 : index]
        target = padded[index]
        counts = model.context_counts.get(context)
        total = model.total_counts.get(context, 0)
        target_count = counts[target] if counts is not None else 0
        probability = (target_count + model.add_k) / (total + (model.add_k * alphabet_size))
        total_log_prob += -math.log2(probability)

    byte_length = len(processed.encode("utf-8"))
    return total_log_prob / max(1, byte_length)
