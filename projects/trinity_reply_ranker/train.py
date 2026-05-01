from __future__ import annotations


WEIGHTS = {
    "sent": 1.0,
    "edited": 0.75,
    "selected": 0.5,
    "ignored": 0.0,
    "rejected": 0.0,
}


def evaluate_trace(trace: dict[str, object]) -> float:
    ranked_ids = [str(candidate_id) for candidate_id in trace["frontier_candidate_ids"]]  # type: ignore[index]
    outcomes = trace["feedback_events"]  # type: ignore[index]
    if not ranked_ids:
        return 0.0

    credit = 0.0
    for outcome in outcomes:
        candidate_id = str(outcome.get("candidate_id") or "")
        if candidate_id not in ranked_ids:
            continue
        rank = ranked_ids.index(candidate_id) + 1
        rank_weight = 1.0 / rank
        disposition = str(outcome.get("disposition") or "").upper()
        if disposition == "SENT_AS_IS":
            credit += rank_weight * WEIGHTS["sent"]
        elif disposition == "EDITED_THEN_SENT":
            credit += rank_weight * WEIGHTS["edited"]
        elif disposition == "SELECTED":
            credit += rank_weight * WEIGHTS["selected"]
        elif disposition == "IGNORED":
            credit += rank_weight * WEIGHTS["ignored"]
        elif disposition in {"REJECTED", "MANUAL_REPLACEMENT", "REWORK_REQUESTED"}:
            credit += rank_weight * WEIGHTS["rejected"]

    return round(min(1.0, credit), 6)
