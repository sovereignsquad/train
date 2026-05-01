# MVP Test

## Purpose

This document defines the current end-to-end MVP validation path.

Use this when you want to confirm the repository is in a locally testable state.

## Preconditions

- `uv` is installed
- `uv sync --extra dev` has been run at least once
- `vibe` is installed if you want the smoke output to confirm agent availability

## Command

```bash
uv sync --extra dev
uv run python scripts/test_mvp.py
```

## What The Smoke Test Does

The smoke test:

1. snapshots the current repository into a temporary clean git worktree
2. starts the local API from that worktree
3. uses an isolated temporary SQLite database
4. checks health, project registry, and the Vibe adapter endpoint
5. verifies migration-backed API startup in a fresh worktree
6. creates a baseline mythology run
7. executes and ratchets that baseline
8. creates a second mythology run
9. executes and ratchets the second run
10. prints the resulting ratchet decisions and project state

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
- first-agent adapter visibility
- migration-backed startup
- worktree-safe startup behavior for isolated proof runs

## Current Limitations

This does not yet prove:

- real mythology model training quality beyond the tiny local benchmark
- broader multi-file ratchet mutation
- long-running heartbeat traffic from a real unattended agent session

For the first real agent-driven proof, use [docs/PROOF_VIBE_CYCLE.md](./PROOF_VIBE_CYCLE.md).
