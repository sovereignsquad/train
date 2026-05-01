# Vibe Proof Cycle

## Purpose

This document records the first real `Mistral Vibe`-driven autonomous experiment cycle completed against the `train` mythology benchmark.

It exists as a durable proof artifact after the temporary clean worktree used by the proof script is removed.

## Command

```bash
uv run python scripts/prove_vibe_cycle.py
```

## Proof Result

Proof date:

- `2026-04-29`

Outcome:

- baseline run accepted
- Vibe edited only `projects/mythology/train.py`
- candidate run accepted
- ratchet committed the improvement
- project state ended clean

Metric result:

- baseline `val_bpb`: `3.526179`
- candidate `val_bpb`: `3.330698`
- delta: `-0.195481`

Agent change captured:

- `ADD_K_SMOOTHING = 0.6`
- `ADD_K_SMOOTHING = 0.1`

Ratchet result:

- decision: `accepted`
- git action: `committed`

## What This Proves

This proof demonstrates that the delivered local platform can:

- launch `Mistral Vibe` through the documented helper path
- constrain the agent to the declared mutable artifact
- evaluate the edited benchmark through the platform runner
- compare the result against best-so-far state
- keep the improvement through the ratchet layer
- end with a clean git state inside an isolated proof worktree

## Operational Notes

- The proof script snapshots the current repository into a temporary clean git worktree before running the cycle.
- The `Vibe` runtime home is separated from the repo-tracked `.vibe/` contract so runtime metadata does not pollute ratchet decisions.
- In this proof, `Vibe` returned exit code `1` with `<vibe_stop_event>Turn limit of 6 reached</vibe_stop_event>`, but the agent still completed a real code edit that the platform evaluated and accepted. Treat that as current CLI behavior, not a platform failure.
