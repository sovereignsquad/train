# Recovery

## Purpose

This document defines the current recovery and rollback behavior for the local operator and ratchet flow.

## Current Ratchet Mutation Policy

The ratchet is currently allowed to mutate git state only under strict constraints.

Allowed:

- commit the declared mutable artifact when a run is accepted
- restore the declared mutable artifact when a run is rejected
- evaluate autonomous changes only when they stay inside the declared mutable artifact set

Not allowed:

- commit arbitrary files
- restore arbitrary files
- mutate the repo when files outside the mutable artifact are dirty
- execute autonomous runs when setup artifacts are dirty
- execute autonomous runs when dependency artifacts are dirty

## Fail-Closed Rule

If the git worktree contains changes outside the declared mutable artifact:

- ratchet mutation is blocked
- the run remains recorded
- the blocked state and error message are persisted on the run record
- manual cleanup is required before retrying

This is intentional.

If autonomous execution begins with guardrail violations:

- the run is marked failed before benchmark execution
- the failure reason is persisted on the run record
- setup, dependency, and unauthorized artifact categories are reported explicitly

## Operator Recovery Contract

The platform now persists operator-visible recovery state on each run:

- `heartbeat_at`
- `lease_expires_at`
- `resumed_from_run_id`
- `resume_count`

The platform also exposes:

- `GET /v1/operator/status`
- `POST /v1/runs/{run_id}/heartbeat`
- `POST /v1/runs/{run_id}/resume`

The current recovery model is:

- a running run holds a lease
- heartbeats extend that lease
- a run becomes stalled when the lease expires
- stalled or failed runs become recoverable only when a known-good project checkpoint exists
- resume creates a new pending run from the last known-good checkpoint and preserves lineage to the interrupted run

## Current Safety Boundary

Today the mutable artifact for the first benchmark is:

- `projects/mythology/train.py`

Protected setup artifacts:

- `projects/mythology/prepare.py`
- `projects/mythology/program.md`
- `projects/mythology/run_benchmark.py`

Protected dependency artifacts:

- `pyproject.toml`
- `uv.lock`

The ratchet should not mutate anything else automatically.

## Recovery Guidance

If ratchet mutation is blocked:

1. inspect `git status`
2. clean or commit unrelated changes manually
3. ensure only the declared mutable artifact is dirty
4. re-run the ratchet step if appropriate

If a run is stalled or failed and recoverable:

1. inspect `GET /v1/operator/status` or the operator UI
2. confirm the project has a known-good checkpoint
3. invoke `POST /v1/runs/{run_id}/resume` or use the UI resume control
4. continue from the new pending run rather than mutating the interrupted run in place

## Current Limitation

The ratchet currently performs:

- accepted-run commit
- rejected-run restore

It does not yet perform:

- multi-file transactional restores
- branch management
- advanced rollback orchestration
- multi-run workflow orchestration from the UI
