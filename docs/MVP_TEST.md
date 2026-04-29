# MVP Test

## Purpose

This document defines the current end-to-end MVP validation path.

Use this when you want to confirm the repository is in a locally testable state.

## Preconditions

- the repository worktree is clean
- `uv` is installed

## Command

```bash
uv sync
uv run python scripts/test_mvp.py
```

## What The Smoke Test Does

The smoke test:

1. starts the local API
2. uses an isolated temporary SQLite database
3. creates a baseline mythology run
4. executes and ratchets that baseline
5. creates a second mythology run
6. executes and ratchets the second run
7. prints the resulting ratchet decisions and project state

## Expected Outcome

Expected shape:

- baseline run is accepted
- second run is rejected when it does not beat best-so-far
- project state reflects:
  - `best_run_id`
  - `best_metric_value`
  - `last_run_id`
  - clean git state

## What This Proves

This confirms the current MVP has:

- a real benchmark project
- deterministic data preparation
- real benchmark execution
- machine-readable metric output
- run ledger persistence
- ratchet decision behavior
- project best-state tracking

## Current Limitations

This does not yet prove:

- real mythology model training quality beyond the tiny local benchmark
- Mistral Vibe adapter integration
- broader multi-file ratchet mutation
- formal database migrations
