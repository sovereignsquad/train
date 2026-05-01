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

- repository-wide rename to `{train}` completed
- native shell overview scoping and release-check error handling corrected
- strategic separation clarified:
  - `{trinity}` runs brains
  - `{train}` improves brains
- managed Python runtime bootstrap and starter project bootstrap generation delivered
- first Trinity-powered `{reply}` optimization proof delivered
- broader git mutation support delivered for multi-artifact project contracts

Primary active issue:

- no blocker remains on the broader git-mutation lane; next lane should move to packaged runtime refresh, unattended heartbeat exercise, or real `{reply}` data integration

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
- `ISSUE-12` completed
- `ISSUE-13` completed
- `ISSUE-14` completed
- `ISSUE-15` completed
- `ISSUE-16` completed
- `ISSUE-17` completed
- follow-on roadmap work should cover:
  - broader git mutation support
  - packaged runtime refresh and update installation
  - real private-data and runtime integration for `{reply}`
  - the next proof after the starter `{reply}` harness

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
- starter reply benchmark project with `project.reply`
- `Mistral Vibe` as the first delivered agent adapter
- provider adapter registry with:
  - `Mistral API`
  - `Ollama`
- repo-local `.vibe/` contract and `scripts/run_vibe.py`
- isolated runtime `VIBE_HOME` under the writable train state directory, separate from the repo-tracked `.vibe/` contract
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
  - app-support runtime and state paths for packaged launches
  - bundled runtime template copied into `train.app`
  - first-launch managed runtime bootstrap through `uv sync --frozen --no-dev`
  - native toolbar-based action placement instead of in-content action clusters
  - responsive project editor sections with file selectors, lists, and structured pickers
  - deterministic app icon generation and bundled `.icns` app icon
  - `{t}`-based app icon and `train.app` bundle naming
  - overview-only shell framing instead of repeating the brand and engine card on every page
  - silent startup update checks that no longer surface a false engine/API error when no release is published
- managed project registry with:
  - reference templates
  - user-defined managed projects
  - CRUD API surface
  - starter workspace bootstrap generation
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
- starter reply benchmark files:
  - `prepare.py`
  - `train.py`
  - `program.md`
  - `run_benchmark.py`
  - `eval_fixture.json`
- replayable `{reply}` proof artifact:
  - `scripts/prove_reply_cycle.py`
  - `docs/PROOF_REPLY_CYCLE.md`
- ratchet mutation support across all changed paths inside declared `autonomous_mutable_artifacts`

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
- `POST /v1/projects/{project_key}/bootstrap`
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
- accepted runs create a git commit when only declared mutable artifacts are dirty
- rejected runs restore changed mutable artifacts cleanly
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
- Trinity-style reply proof through `uv run python scripts/prove_reply_cycle.py`
- `npm audit --omit=dev` with zero vulnerabilities in `apps/web`
- `npm run lint`
- `npm run build`
- `uv run pytest`
- `uv run pytest tests/test_ratchet.py`
- `uv run pytest tests/test_projects.py`
- `uv run ruff check .`
- the repository can be validated end to end with `uv run python scripts/test_mvp.py`
- `uv run python projects/reply/run_benchmark.py --budget-seconds 60 --run-id 1`
- `swift build -c release` in `apps/macos`
- app bundle creation through `apps/macos/Scripts/build-bundle.sh`
- packaged runtime template included in `train.app`
- native-shell engine launch path fixed for non-interactive app environments
- managed-project CRUD verified through the live HTTP API
- managed-project starter bootstrap verified through unit coverage
- native shell rebuilt after UI recovery with warning-free Swift build
- repository, package, bundle, and remote rename from `autotrain` to `train`
- native shell rebuilt after overview scoping and update-check error handling fixes

## Current Gaps

Still missing on the critical path:

- longer unattended heartbeat exercise by a real agent session
- packaged desktop update installation beyond release checks
- real private-data and runtime integration for the eventual `{reply}` production lane

## Immediate Next Steps

1. decide whether packaged runtime refresh or unattended heartbeat exercise is the next engine lane
2. decide when to replace the starter `{reply}` fixture with real private-data ingestion
3. decide whether the Vibe turn-limit exit behavior deserves its own follow-up issue
4. define the next honest proof after `{reply}` once the real data contract exists
5. decide whether multi-artifact managed-project bootstrap examples should be added next

## Current Risks

- heartbeat and resume semantics are implemented, but unattended lease refresh is not yet exercised by a long-running agent loop
- `Vibe` currently exits with a non-zero code when the configured turn limit is reached, even if it completed useful work
- the native shell does not yet install or update the Python engine as a self-contained packaged desktop dependency
- the starter `reply` benchmark is local and deterministic, and the proof mutation is intentionally fixture-aware until real private `{reply}` data and runtime integration exist

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

- packaged desktop refinement, unattended heartbeat exercise, or real `{reply}` data integration, according to board priority
