from __future__ import annotations


WEIGHTS = {
    "quality_score": 0.34,
    "urgency_score": 0.24,
    "freshness_score": 0.18,
    "feedback_score": 0.14,
    "ice_score": 0.10,
}


def frontier_score(candidate: dict[str, float | int | str]) -> float:
    quality = _clamp_percent(candidate["quality_score"])
    urgency = _clamp_percent(candidate["urgency_score"])
    freshness = _clamp_percent(candidate["freshness_score"])
    feedback = _clamp_percent(candidate["feedback_score"])
    ice = _ice_score(candidate)
    return round(
        (quality * WEIGHTS["quality_score"])
        + (urgency * WEIGHTS["urgency_score"])
        + (freshness * WEIGHTS["freshness_score"])
        + (feedback * WEIGHTS["feedback_score"])
        + (ice * WEIGHTS["ice_score"]),
        6,
    )


def rank_candidates(candidates: list[dict[str, float | int | str]]) -> list[str]:
    ranked = sorted(
        candidates,
        key=lambda candidate: (-frontier_score(candidate), str(candidate["candidate_id"])),
    )
    return [str(candidate["candidate_id"]) for candidate in ranked]


def evaluate_case(case: dict[str, object]) -> float:
    expected = [str(candidate_id) for candidate_id in case["expected_order"]]  # type: ignore[index]
    ranked = rank_candidates(case["candidates"])  # type: ignore[index]
    matches = sum(1 for left, right in zip(ranked, expected, strict=False) if left == right)
    return matches / len(expected)


def _ice_score(candidate: dict[str, float | int | str]) -> float:
    impact = _clamp_ice(candidate["impact"])
    confidence = _clamp_ice(candidate["confidence"])
    ease = _clamp_ice(candidate["ease"])
    return ((impact * confidence * ease) / 1000.0) * 100.0


def _clamp_percent(value: float | int | str) -> float:
    return max(0.0, min(100.0, float(value)))


def _clamp_ice(value: float | int | str) -> float:
    return max(1.0, min(10.0, float(value)))
