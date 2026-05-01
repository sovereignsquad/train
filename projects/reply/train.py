from __future__ import annotations

import re


def draft_reply(example: dict[str, str]) -> str:
    language = example["language"]
    intent = example["intent"]

    if language == "hu":
        if intent == "business_decision":
            return "Én egy kicsit várnék, és előbb a prioritásokat tisztáznám."
        if intent == "personal":
            return "Ez rendben van, adj magadnak egy kis időt, és nézd meg nyugodtan a tényeket."
        return "Rendben, köszönöm. Nézd meg, és utána beszéljünk róla."

    if intent == "business_decision":
        return "I would wait a bit and make sure the priorities are clear first."
    if intent == "personal":
        return "That is normal. Give it a little time and focus on the facts."
    return "Perfect, thank you. Review it when you can and we will discuss it after."


def score_reply(candidate: str, gold_reply: str) -> float:
    candidate_tokens = _tokenize(candidate)
    gold_tokens = _tokenize(gold_reply)

    if not candidate_tokens or not gold_tokens:
        return 0.0

    overlap = len(candidate_tokens & gold_tokens)
    precision = overlap / len(candidate_tokens)
    recall = overlap / len(gold_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _tokenize(text: str) -> set[str]:
    normalized = re.sub(r"[^\w\s]", " ", text.lower(), flags=re.UNICODE)
    return {token for token in normalized.split() if token}

