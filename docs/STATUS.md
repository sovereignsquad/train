# Status

## Purpose

This is the current status document for the repository.

It is the short-term execution SSOT for:

- current phase
- active issue
- what is already done
- what is blocked
- what should happen next

Update this document whenever the active implementation state changes materially.

## Current Phase

Phase:

- ratchet and ledger foundation

Primary active issue:

- `ISSUE-5`

Board intent:

- `ISSUE-2` completed
- `ISSUE-4` completed
- `ISSUE-5` in progress

## Current Reality

The repository currently has:

- open-source and operating docs
- Apache-2.0 licensing
- repository contract docs
- Python project scaffold
- `FastAPI` local API
- `SQLite` local state
- project registry with `project.mythology`
- run lifecycle endpoints:
  - create
  - start
  - complete
  - execute
  - ratchet
  - fetch
- project state ledger
- best-score comparison model
- git-state capture during ratchet evaluation
- placeholder mythology benchmark files:
  - `prepare.py`
  - `train.py`
  - `program.md`
  - `run_benchmark.py`

## Verified Working

Verified locally:

- `uv sync`
- API startup with `uvicorn`
- `GET /health`
- `GET /v1/projects`
- `POST /v1/runs`
- `POST /v1/runs/{id}/start`
- `POST /v1/runs/{id}/complete`
- `POST /v1/runs/{id}/execute`
- `POST /v1/runs/{id}/ratchet`
- `GET /v1/project-states`
- `GET /v1/runs/{id}`
- end-to-end bounded subprocess execution through the placeholder mythology benchmark
- best-score updates across multiple runs with accepted and rejected outcomes
- accepted runs create a git commit when only the mutable artifact is dirty
- rejected runs restore the mutable artifact cleanly
- unrelated dirty files block ratchet mutation with a fail-closed response

## Current Gaps

Still missing on the critical path:

- real mythology benchmark implementation beyond placeholder execution
- broader git mutation support beyond the single declared mutable artifact

## Immediate Next Steps

1. Decide whether `ISSUE-5` is complete enough to close.
2. Replace placeholder mythology execution with real benchmark behavior in later work.
3. Improve failure-path handling and migration strategy.
4. Decide whether broader git mutation support belongs in a separate issue.

## Current Risks

- the local DB schema currently uses a dev-safe reset instead of formal migrations
- the mythology benchmark currently uses a placeholder execution script, not a real training loop
- git mutation currently supports only the declared mutable artifact path

## Blockers

Current blockers:

- none for continuing engine work

## Resume Point

If resuming work, start by reading:

1. `docs/STATUS.md`
2. `docs/HANDOVER.md`
3. `docs/BRAIN.md`
4. `AGENTS.md`

Then continue on:

- `ISSUE-5`
