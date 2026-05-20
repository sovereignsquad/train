# Integration Surface

## Purpose

This document records the current app-and-service relation map for `{train}`.

It distinguishes between:

- current runtime or tooling relations that the repo actually uses
- reverse relations where other apps or systems consume `{train}`
- planned hosted-leg references that are documented but not active runtime dependencies today

It also captures the latest local health-check snapshot for those relations.

Current hardening surfaces now present in the repo:

- `uv run python -m train_core.cli doctor`
- `uv run python -m train_core.cli check-training-readiness`
- `uv run python scripts/check_operator_clients.py`
- `uv run python scripts/prove_trinity_train_handoff.py`
- `uv run python scripts/check_packaged_release_contract.py`

## Current Forward Relations

These are apps, tools, or services `{train}` currently requires or references.

### Core Local Runtime

- `train-api`
  - local `FastAPI` service started through `uvicorn`
- `SQLite`
  - default local state and metadata store
- `uv`
  - Python dependency and runtime bootstrap tool
- filesystem artifact storage
  - local-first run outputs, logs, and state files

### Operator App Surfaces

- `apps/web`
  - `Next.js` + `Mantine` operator UI that reads `{train}` API contracts
- `apps/macos`
  - native `SwiftUI` / `AppKit` shell that supervises or attaches to the local engine

### Agent And Provider Relations

- `Mistral Vibe`
  - first-class agent adapter exposed as `mistral-vibe`
- `Mistral API`
  - hosted provider adapter exposed as `mistral-api`
- `Ollama`
  - local provider adapter exposed as `ollama`
- `mlx-lm`
  - first offline fine-tuning worker backend for the Apple-Silicon training lane

### Delivery And Update Relations

- `GitHub Issues`
  - primary work reference and roadmap system
- `GitHub Project`
  - delivery planning system
- `GitHub Releases`
  - current macOS update-check source through the GitHub REST API

### Cross-Repo Runtime Relation

- `{trinity}`
  - exports bounded traces and bundles that `{train}` consumes offline
  - may call `{train}` by API or CLI for bounded proposal and skeptical-review work
- `{reply}`
  - product context around the `{trinity}` runtime seam
  - referenced architecturally, but not currently verified here as a direct caller of `{train}`

## Reverse Relations

These are apps or systems that currently require or reference `{train}`.

### Repo-Internal Consumers

- `apps/web`
  - calls `/health`, `/v1/projects`, `/v1/project-states`, `/v1/runs`, `/v1/agents/mistral-vibe`, `/v1/providers/mistral-api`, `/v1/providers/ollama`, and `/v1/operator/status`
- `apps/macos`
  - starts or attaches to the local engine, polls `/health`, and drives the native operator workflow from API state
- proof and smoke scripts
  - `scripts/test_mvp.py`
  - `scripts/prove_reply_cycle.py`
  - `scripts/prove_second_project.py`
  - `scripts/prove_vibe_cycle.py`
  - `scripts/check_operator_clients.py`
  - `scripts/prove_trinity_train_handoff.py`
  - `scripts/check_packaged_release_contract.py`

### External Consumer

- `{trinity}`
  - documented external runtime consumer of `{train}` proposal and review surfaces

## Planned But Not Active Runtime Relations

These are referenced in architecture docs but are not current local runtime dependencies that this repo exercised in the latest audit.

- `Vercel`
  - planned hosted web deployment target
- `MongoDB Atlas`
  - planned hosted shared persistence

They should not be described as required for the current local-first implementation path.

## Health Check Snapshot

Audit date:

- `2026-05-20`

Environment:

- local workspace at `/Users/Shared/Projects/train`

### Passed

- `train-api` local smoke path
  - `uv run python scripts/test_mvp.py`
  - result: passed
  - evidence:
    - `/health` returned `{"status":"ok","service":"train-api","environment":"local"}`
    - project registry responded
    - run execution and ratchet flow completed
- `Mistral Vibe` adapter status
  - `uv run python -c "... get_agent_status('mistral-vibe') ..."`
  - result: passed
  - evidence:
    - executable resolved at `/Users/moldovancsaba/.local/bin/vibe`
    - version `vibe 2.9.0`
    - repo-local `.vibe` contract files present
    - `MISTRAL_API_KEY` configured in this environment
- provider adapter checks
  - `uv run python scripts/check_providers.py`
  - result: passed
  - evidence:
    - `Mistral API` reachable with live model listing
    - `Ollama` reachable at `http://127.0.0.1:11434` with live model listing
- web operator surface
  - `cd apps/web && npm run build`
  - result: passed
- native macOS shell
  - `cd apps/macos && swift build -c release`
  - result: passed
- `{trinity}` bounded seam tests
  - `uv run pytest tests/test_trinity_reply_policy_service.py tests/test_trinity_spot_policy_service.py tests/test_trinity_skeptical_eval.py tests/test_trinity_training_bundle_loader.py tests/test_trinity_spot_training_bundle_loader.py tests/test_trinity_scope.py`
  - result: passed
- baseline adapter and provider contract tests
  - `uv run pytest tests/test_agents.py tests/test_providers.py tests/test_config.py`
  - result: passed
- local repo-presence check
  - `/Users/Shared/Projects/trinity`
  - result: present

### Passed After Hardening

- `mlx-lm`
  - `uv sync --extra dev --extra local-training`
  - `uv run python -c "import importlib.util; print(importlib.util.find_spec('mlx_lm') is not None)"`
  - result: installed and importable in this environment
- offline training doctor
  - `uv run python -m train_core.cli doctor --workflow training --output-format summary`
  - result: passed against a live local API on `2026-05-20`
- training-spec readiness
  - `uv run python -m train_core.cli check-training-readiness --spec-key cycle-spec --spec-version 2026-05-19.1 --output-format summary`
  - result: passed
- `GitHub Releases` update source
  - `GET https://api.github.com/repos/sovereignsquad/train/releases/latest`
  - result: reachable and returns published release `v0.1.0`
- packaged release preflight
  - `uv run python scripts/check_packaged_release_contract.py`
  - result: passed
- published release assets
  - [v0.1.0](https://github.com/sovereignsquad/train/releases/tag/v0.1.0)
  - result:
    - `train-v0.1.0-macos-app.zip`
    - `train-v0.1.0-macos-app.zip.sha256`

### Degraded Or Missing

- public macOS distribution signing
  - `codesign -dv --verbose=4 apps/macos/dist/train.app`
  - `spctl --assess --type execute --verbose apps/macos/dist/train.app`
  - result:
    - bundle is ad-hoc signed
    - Gatekeeper rejects it
  - meaning:
    - the repo can publish packaged app assets now
    - the release is not yet Developer ID signed or notarized

### Not Fully Proven By This Audit

- repeatable multi-bundle or multi-family `{trinity}` cross-repo invocation
  - the repo now has one live cross-repo proof where `{trinity}` exports a bundle and calls a running `{train}` API
  - broader runtime families beyond the current bounded proof are not yet exercised end to end
- direct `{reply}` to `{train}` consumption
  - `{reply}` is part of the architecture context
  - this repo does not currently prove a direct `{reply}` caller relation
- hosted leg relations
  - `Vercel`
  - `MongoDB Atlas`
  - they remain planned-only references in current docs

## Hardening Status

Implemented from the recommended audit follow-up:

- first-class `doctor` command for relation readiness
- dedicated offline training readiness check
- live operator-client contract smoke script against the local API
- live cross-repo `{trinity}` to `{train}` proof script
- configurable macOS GitHub-release updater contract

Still not fully hardened:

- `mlx-lm` is still environment-dependent even though it is now installed on the audited machine
- the updater contract now has a published release flow, but the shipped app asset is still not notarized
- the daily self-learning loop is bounded and explicit, but not scheduled or promotion-automated

## Audit View

### What Looks Healthy

- the current local-first engine relation is real, not aspirational
- both shipped operator surfaces still build against the present repo contracts
- the provider adapter boundary is working against both a hosted and a local model backend in this environment
- the agent adapter boundary is working with a real installed `vibe` executable and repo-local contract files
- the bounded `{trinity}` seams have real test coverage and do not appear to be doc-only

### What Needs Hardening

- the relation inventory is spread across multiple docs and code paths
- the repo still needs one tighter SSOT for relation health instead of repeating state across README, setup, status, and integration docs
- the offline training lane now has readiness and doctor surfaces, but still lacks a first-class adapter-evaluation and promotion gate
- the GitHub release path is live, but the packaged desktop asset is not yet signed or notarized for end-user distribution
- `{trinity}` integration is contract-tested more strongly than it is end-to-end runtime-proven
- planned hosted-leg references can still be mistaken for current hard dependencies if docs drift

### Recommendations

1. Keep current and planned relations explicitly separate in docs.
   - current: `Mistral Vibe`, `Mistral API`, `Ollama`, `GitHub Releases`, `apps/web`, `apps/macos`, `{trinity}`
   - planned: `Vercel`, `MongoDB Atlas`
2. Finish desktop distribution hardening.
   - add Developer ID signing
   - add notarization
   - keep release assets attached to GitHub Releases
3. Add compatibility tests for operator clients against API contracts.
   - web build catches type-level drift
   - native build catches compile drift
   - a lightweight client-contract smoke test would catch response-shape regressions earlier
4. Add one adapter-evaluation and promotion gate on top of the current offline training lane.
   - run evaluation after training
   - keep packaging conditional on evidence
   - keep adoption explicit

### Recommendation Priority

If only three hardening moves happen next, they should be:

1. finish signed/notarized macOS distribution
2. add one adapter-evaluation and promotion gate for offline training
3. keep the live `{trinity}` proof and operator-client smoke checks in regular verification
