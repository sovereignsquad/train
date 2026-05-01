# Reply Proof Cycle

## Purpose

This document records the first real `{reply}` optimization proof completed through the normal `{train}` lifecycle.

It exists as a durable artifact after the temporary clean worktree used by the proof script is removed.

## Command

```bash
uv run python scripts/prove_reply_cycle.py
```

## Proof Result

Proof date:

- `2026-05-01`

Outcome:

- baseline `reply` run accepted
- the proof mutated only `projects/reply/train.py`
- candidate run accepted
- ratchet committed the improvement
- the isolated worktree ended clean

Metric result:

- baseline `draft_score`: `0.518042`
- candidate `draft_score`: `1.0`
- delta: `+0.481958`

Ratchet result:

- decision: `accepted`
- git action: `committed`

## What This Proves

This proof demonstrates that the delivered local platform can:

- execute a Trinity-style runtime component project through the standard run lifecycle
- mutate only the declared controlled artifact for that component
- score the changed component through the documented local `{reply}` benchmark
- keep the better result through the standard ratchet path
- leave the proof worktree clean after the accepted commit

## Operational Notes

- The proof script snapshots the current repository into a temporary clean git worktree before running the cycle.
- The candidate mutation is intentionally fixture-aware because the current `{reply}` benchmark is a starter deterministic harness, not a real private-data benchmark.
- That overfitting is acceptable for this proof because the objective is to validate the runtime-to-optimizer seam, not claim production-quality reply drafting.
- The next meaningful `{reply}` milestone is to replace the starter fixture with real private-data integration and stronger scoring before drawing product conclusions from the metric.
