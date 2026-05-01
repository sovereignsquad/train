# Handover

## Purpose

This document exists so work can be resumed cleanly by:

- the same developer later
- another developer
- another coding agent

It is the short-term transfer document.

## How To Use

When ending a meaningful work session, update:

- what changed
- what was verified
- what remains next
- what must be watched carefully

Keep this document concise and current.

## Current Handover

### What Changed Last

Last completed increment:

- repository-wide rename to `{train}`
- native shell overview scoping and startup update-check fix
- strategic architecture clarification:
  - `{trinity}` runs brains
  - `{train}` improves brains

Implemented:

- `Mistral Vibe` adapter surface:
  - repo-local `.vibe/` contract
  - `GET /v1/agents`
  - `GET /v1/agents/{agent_key}`
  - `GET /v1/agents/{agent_key}/launch-plan`
  - `scripts/run_vibe.py`
- formal Alembic migration startup replacing the dev-safe schema reset path
- `Next.js` + `Mantine` operator UI in `apps/web`
- updated MVP smoke test that snapshots the current worktree into a temporary clean git worktree
- proof runner in `scripts/prove_vibe_cycle.py`
- runtime `VIBE_HOME` isolation so Vibe metadata no longer blocks ratchet mutation
- project-level autonomous guardrails in `core/train_core/guardrails.py`
- pre-execution guardrail enforcement in `core/train_core/runner.py`
- ratchet-side guardrail classification in `core/train_core/ratchet.py`
- provider adapter registry in `core/train_core/providers.py`
- provider API surfaces:
  - `GET /v1/providers`
  - `GET /v1/providers/{provider_key}`
- live provider probe script:
  - `scripts/check_providers.py`
- operator recovery layer in `core/train_core/operator.py`
- operator API surfaces:
  - `GET /v1/operator/status`
  - `POST /v1/runs/{run_id}/heartbeat`
  - `POST /v1/runs/{run_id}/resume`
- run heartbeat, lease, and resume lineage state in the DB
- operator UI provider status cards
- operator UI resume control for recoverable runs
- hardened worktree proof harnesses with startup log capture
- second benchmark project in `projects/helpdesk/`
- second proof runner in `scripts/prove_second_project.py`
- native macOS app scaffold in `apps/macos/`
- local engine supervisor and API dashboard in the Swift shell
- bundle scripts for local desktop artifacts
- release-check scaffold against GitHub releases
- deterministic `uv` discovery with `TRAIN_UV_EXECUTABLE` override support
- attach-to-existing-engine or next-free-port fallback when `8420` is already occupied
- managed project registry in the API with create, read, update, and delete support
- dedicated native Projects workspace separating managed projects from built-in templates
- moved primary app actions into the native toolbar
- replaced raw artifact blobs with file selectors and editable artifact lists
- restructured the project editor into responsive native sections
- replaced the Projects page card wall with a native list-detail layout
- added a deterministic app icon generation pipeline and embedded `.icns` bundle icon
- renamed the core package, API package, repo-local Vibe contract, native app target, bundle, and GitHub remote from `autotrain` to `{train}`
- refreshed the generated app icon from the old `AT` monogram to a `{t}` mark aligned with the new app name
- recorded the UI failure and recovery standard in `docs/UI_UX_RECOVERY.md`
- scoped the `{train}` brand header and engine supervisor card back to the Overview page instead of every page
- changed the startup GitHub release check to run silently so a missing release does not show a false orange API error
- project contract metadata for:
  - autonomous mutable artifacts
  - setup artifacts
  - dependency artifacts
  - min/max budget seconds
- strategic repo split:
  - `{trinity}` is the runtime workflow repository
  - `{train}` remains the bounded optimizer for project artifacts and runtime components
- new roadmap issues opened for the next lane:
  - `ISSUE-12` Trinity-aware idea-to-project onboarding
  - `ISSUE-13` managed-project bootstrap generation
  - `ISSUE-14` runtime-to-optimizer contract for systems such as `{trinity}`
  - `ISSUE-15` the first `{reply}` template
  - `ISSUE-16` the first local `{reply}` benchmark contract
  - `ISSUE-17` the first Trinity-powered optimization proof

### What Was Verified

Verified:

- `uv run ruff check .`
- `uv run pytest`
- `npm run lint`
- `npm run build`
- `npm audit --omit=dev`
- `uv run python scripts/test_mvp.py`
- `uv run python scripts/prove_vibe_cycle.py`
- `vibe --version`
- canonical Vibe launch-plan generation via `scripts/run_vibe.py --print-only --json`
- accepted autonomous improvement:
  - `ADD_K_SMOOTHING = 0.6`
  - `ADD_K_SMOOTHING = 0.1`
  - `val_bpb 3.526179 -> 3.330698`
- guardrail unit coverage for:
  - budget enforcement
  - setup artifact blocking
  - dependency artifact classification
  - unauthorized artifact blocking
- provider adapter coverage for:
  - hosted Mistral status probing
  - local Ollama status probing
  - API provider serialization
- operator coverage for:
  - stalled-run detection
  - heartbeat lease refresh
  - safe resume from known-good checkpoints
- second-project coverage for:
  - maximize-metric ratchet semantics
  - second project registry reuse
  - second proof through the Ollama provider surface
- native-shell verification for:
  - `swift build -c release`
  - app bundle creation
  - bundle signature validation
  - engine launch path in non-interactive app context
- live HTTP CRUD verification for managed projects
- warning-free Swift rebuild after the UI recovery pass
- full rename validation for Python, web, macOS bundle, MVP smoke test, and GitHub remote

### What Needs To Happen Next

Next expected work:

1. implement runtime bootstrap inside the native shell
2. remove remaining repo-root assumptions for packaged use
3. decide whether managed-project folder bootstrapping belongs before or after packaged desktop delivery
4. decide when to exercise heartbeat refresh in a longer unattended agent session
5. add the Trinity-aware idea-to-project and `{reply}` template roadmap once runtime bootstrap priority is settled

### Watch Carefully

- keep engine code generic
- do not hardcode mythology-specific logic into `core/`
- keep agent adapter work out of runner core
- keep provider adapter work out of runner and ratchet core
- keep the UI as an operator surface, not a second workflow engine
- preserve the proof artifact and keep future proofs equally reproducible
- remember that Vibe currently reports turn-limit stop events with a non-zero exit code
- keep setup/dependency protection explicit in new project definitions
- keep resume semantics tied to known-good project checkpoints, not ad hoc local edits
- keep the Swift shell thin and do not migrate engine logic out of Python
- keep packaged desktop concerns separate from engine and benchmark contracts
- keep reference templates distinct from managed user projects in both API and UI
- keep desktop actions in the toolbar unless there is a strong native UX reason not to
- keep `{trinity}` runtime responsibilities out of `{train}` core while still making runtime components optimizable through project contracts

### If You Only Have 30 Minutes

Do this:

- verify the agent endpoints and launch-plan output
- verify `scripts/check_providers.py`
- run the smoke test
- verify provider, operator, guardrail, and second-project tests
- verify `swift build -c release` in `apps/macos`
- verify `bash apps/macos/Scripts/build-bundle.sh`
- update `docs/STATUS.md`

### If You Have A Full Session

Do this:

- run the full verification stack
- close the second-proof issue
- choose the next post-shell lane
