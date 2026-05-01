# Second Proof

## Purpose

This document records the second platform-validation pass for `train`.

It proves that the platform works beyond:

- the first benchmark project
- the first metric direction
- the first integration path

## What Was Added

Second project:

- `projects/helpdesk`

Second integration surface exercised in the proof:

- `ollama` provider adapter

## Why This Matters

The first benchmark, `mythology`, uses:

- character-level language modeling
- `val_bpb`
- `minimize`

The second benchmark, `helpdesk`, uses:

- deterministic intent classification
- `macro_f1`
- `maximize`

That difference is enough to test whether the engine, ratchet, guardrails, and run ledger are actually reusable.

## Proof Command

```bash
uv run python scripts/prove_second_project.py
```

## What The Proof Does

The proof:

1. snapshots the repository into a temporary clean worktree
2. starts the API against an isolated SQLite database
3. checks the second provider surface through `GET /v1/providers/ollama`
4. creates a `helpdesk` run
5. executes the benchmark
6. ratchets the result
7. prints the resulting project state

## Current Result

The proof confirmed:

- `helpdesk` is registered through the existing project contract
- the runner executes the second project without engine changes
- the ratchet accepts a `maximize` metric correctly
- the second provider surface is queried through the existing provider adapter boundary

## Reuse Observed

Reused unchanged:

- run lifecycle API
- guardrail enforcement
- subprocess runner
- ratchet decision logic
- project state ledger
- provider status surface

Project-specific only:

- `projects/helpdesk/prepare.py`
- `projects/helpdesk/train.py`
- `projects/helpdesk/run_benchmark.py`
- `projects/helpdesk/program.md`

## Remaining Limitations

- the second proof does not yet exercise a second agent adapter
- the ratchet still assumes a single declared mutable artifact
- the helpdesk benchmark is intentionally small and deterministic, not a production dataset
