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

- repository-wide rename to `train` completed

Primary active issue:

- no blocker remains on the renamed shell scaffold; next lane should move to runtime bootstrap and packaged desktop delivery

Board intent:

- `ISSUE-2` completed
- `ISSUE-3` completed
- `ISSUE-4` completed
- `ISSUE-5` completed
- `ISSUE-6` completed
- `ISSUE-7` completed
- `ISSUE-8` completed
- `ISSUE-9` completed
- `ISSUE-10` completed
- `ISSUE-11` completed

## Current Reality

The repository currently has:

- open-source and operating docs
- Apache-2.0 licensing
- repository contract docs
- Python project scaffold
- `FastAPI` local API
- native macOS shell scaffold in `apps/macos`
- Alembic-backed `SQLite` local state
- project registry with `project.mythology`
- second benchmark project with `project.helpdesk`
- `Mistral Vibe` as the first delivered agent adapter
- provider adapter registry with:
  - `Mistral API`
  - `Ollama`
- repo-local `.vibe/` contract and `scripts/run_vibe.py`
- isolated runtime `VIBE_HOME` under `artifacts/local/vibe-home`
- machine-checkable autonomous guardrails:
  - mutable-artifact restriction
  - setup-artifact protection
  - dependency-artifact protection
  - project budget bounds
- operator recovery baseline:
  - heartbeat leases
  - stalled-run detection
  - safe resume from a known-good checkpoint
- `Next.js` + `Mantine` operator UI with recovery visibility and resume control
- native SwiftUI operator shell with:
  - local process supervision
  - API-backed dashboard
  - recovery actions
  - release-check scaffold
  - deterministic `uv` executable resolution with override support
  - attach/fallback behavior when the preferred API port is already occupied
  - native toolbar-based action placement instead of in-content action clusters
  - responsive project editor sections with file selectors, lists, and structured pickers
  - deterministic app icon generation and bundled `.icns` app icon
  - `T`-based app icon and `Train.app` bundle naming
- managed project registry with:
  - reference templates
  - user-defined managed projects
  - CRUD API surface
  - dedicated native Projects workspace
- run lifecycle endpoints:
  - create
  - start
  - complete
  - execute
  - ratchet
  - fetch
  - agent status
  - agent launch-plan
  - provider status
  - operator status
- project state ledger
- best-score comparison model
- git-state capture during ratchet evaluation
- a reproducible MVP smoke test
- real mythology benchmark files:
  - `prepare.py`
  - `train.py`
  - `program.md`
  - `run_benchmark.py`
- real helpdesk benchmark files:
  - `prepare.py`
  - `train.py`
  - `program.md`
  - `run_benchmark.py`

## Verified Working

Verified locally:

- `uv sync --extra dev`
- API startup with `uvicorn`
- `GET /health`
- `GET /v1/agents`
- `GET /v1/agents/mistral-vibe`
- `GET /v1/providers`
- `GET /v1/providers/mistral-api`
- `GET /v1/providers/ollama`
- `GET /v1/operator/status`
- `GET /v1/projects`
- `GET /v1/projects/templates`
- `GET /v1/projects/{project_key}`
- `POST /v1/projects`
- `PUT /v1/projects/{project_key}`
- `DELETE /v1/projects/{project_key}`
- `POST /v1/runs`
- `POST /v1/runs/{id}/start`
- `POST /v1/runs/{id}/heartbeat`
- `POST /v1/runs/{id}/complete`
- `POST /v1/runs/{id}/execute`
- `POST /v1/runs/{id}/ratchet`
- `POST /v1/runs/{id}/resume`
- `GET /v1/project-states`
- `GET /v1/runs/{id}`
- end-to-end bounded subprocess execution through the real mythology benchmark
- end-to-end bounded subprocess execution through the real helpdesk benchmark
- best-score updates across multiple runs with accepted and rejected outcomes
- accepted runs create a git commit when only the mutable artifact is dirty
- rejected runs restore the mutable artifact cleanly
- unrelated dirty files block ratchet mutation with a fail-closed response
- blocked ratchet attempts persist `git_action=blocked` and a recovery message on the run record
- `vibe --version`
- canonical Vibe plan generation through `scripts/run_vibe.py`
- one real Vibe-driven autonomous experiment cycle through `scripts/prove_vibe_cycle.py`
- budget bounds enforced through the project contract
- dependency and setup artifact mutations fail closed before execution
- live provider probes through `scripts/check_providers.py`
- recoverable-run summaries through `GET /v1/operator/status`
- safe resume lineages through `POST /v1/runs/{id}/resume`
- second-project proof through `uv run python scripts/prove_second_project.py`
- `npm audit --omit=dev` with zero vulnerabilities in `apps/web`
- `npm run lint`
- `npm run build`
- `uv run pytest`
- `uv run ruff check .`
- the repository can be validated end to end with `uv run python scripts/test_mvp.py`
- `swift build -c release` in `apps/macos`
- app bundle creation through `apps/macos/Scripts/build-bundle.sh`
- native-shell engine launch path fixed for non-interactive app environments
- managed-project CRUD verified through the live HTTP API
- native shell rebuilt after UI recovery with warning-free Swift build
- repository, package, bundle, and remote rename from `autotrain` to `train`

## Current Gaps

Still missing on the critical path:

- broader git mutation support beyond the single declared mutable artifact
- longer unattended heartbeat exercise by a real agent session
- managed Python runtime bootstrap inside the native shell
- packaged desktop state bootstrap independent of repo-root assumptions
- packaged desktop update installation beyond release checks

## Immediate Next Steps

1. implement native runtime bootstrap and packaged app-support state paths
2. decide whether the broader git mutation issue or runtime packaging has priority after that
3. decide whether the Vibe turn-limit exit behavior deserves its own follow-up issue
4. decide when heartbeat integration should be exercised by a longer unattended agent session

## Current Risks

- git mutation currently supports only the declared mutable artifact path
- heartbeat and resume semantics are implemented, but unattended lease refresh is not yet exercised by a long-running agent loop
- `Vibe` currently exits with a non-zero code when the configured turn limit is reached, even if it completed useful work
- the native shell currently assumes a repo-root development workflow and does not yet ship a managed Python runtime
- the native shell does not yet install or update the Python engine as a self-contained packaged desktop dependency
- managed projects store contract metadata, but they do not yet ship a turnkey project-folder bootstrap generator

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

- native runtime bootstrap and packaged desktop delivery, unless roadmap priority changes
