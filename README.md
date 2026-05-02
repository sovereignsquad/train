# {train}

`train` is a provider-neutral autonomous optimization platform.

It improves bounded components of larger systems through explicit experiments, automatic scoring, and keep-or-reject ratcheting.

In the current architecture:

- `{reply}` is the product
- `{trinity}` runs brains
- `{train}` improves brains

That means:

- `{reply}` owns the user-facing omnichannel workflow
- `{trinity}` owns the runtime candidate-processing workflow
- `{train}` owns bounded optimization of declared components

The system is inspired by the `autoresearch` pattern:

- one controlled mutable artifact
- one automatic score
- one bounded experiment loop
- one ratchet that keeps improvements and reverts regressions

The first reference benchmark used mythology / folktales training to prove the loop, but the platform is intended to support other optimization domains later, including bounded components of external runtime workflows such as `{trinity}`.

The repository now also includes a second reference benchmark:

- `helpdesk`, a deterministic intent-classification project with a `maximize` metric

The repository now also includes a starter `{trinity}`-style `{reply}` benchmark:

- `reply`, a deterministic local reply-drafting project with a `maximize` metric and local-only data override support

The repository also now includes a native macOS operator shell:

- `apps/macos`, a SwiftUI desktop shell that supervises the local engine, exposes operator status, and prepares the path toward packaged desktop delivery
- a managed project registry with reference templates and user-defined project contracts
- a theme/readability contract that keeps day and night mode aligned with the shared Constellation semantics

## Overview

For the high-level overview of what `{train}` is, how it works, what it can do, and what it is not, read:

- [TRAIN_OVERVIEW.md](./TRAIN_OVERVIEW.md)

## License

This project is licensed under `Apache-2.0`.

That is the default for the project because it is:

- permissive
- contribution-friendly
- appropriate for commercial and non-commercial reuse
- stronger than `MIT` for this project because it includes an explicit patent grant

See [LICENSE](./LICENSE).

## Platform Shape

The core platform is split into four layers:

1. Experiment engine
2. Project contract
3. Agent adapters
4. Provider adapters

These layers must stay separate.

### Experiment Engine

Owns:

- run budget
- metric parsing
- result records
- ratchet keep/revert logic
- experiment ledger
- recovery boundaries

### Project Contract

Every project should define:

- setup logic
- one controlled mutable artifact
- `program.md`
- one automatic metric
- bounded run entrypoint
- logs and artifacts

Projects may optimize:

- a standalone benchmark artifact
- a bounded runtime component from another system such as `{trinity}`

The contract stays the same either way: one controlled mutable artifact, one bounded run, and one automatic score.

### Agent Adapters

Agent adapters drive code-editing and execution workflows.

Delivered first adapter:

- `Mistral Vibe` with a repo-local `.vibe/` contract, API status surface, and canonical launch helper

Planned later:

- additional agent adapters such as `Cursor`

### Provider Adapters

Provider adapters expose model backends to the platform when needed.

Delivered first adapters:

- `Mistral API` as the first hosted provider path
- `Ollama` as the first local open-source provider path

Local open-source models are supported through adapters, but they are not required to start building the platform.

## Recommended Stack

### Core Platform

- `Python 3.12+`
- `FastAPI`
- `Pydantic`
- `uv`
- local subprocess-based job execution

### Local Persistence

- `SQLite` for local metadata and state
- local filesystem for logs, samples, and experiment artifacts

### Web UI / Control Plane

- `Next.js`
- `Mantine`

### Native Desktop Shell

- `Swift`
- `SwiftUI`
- `SwiftPM`

### Hosted / Online Leg

- `Vercel` for the web surface
- `MongoDB Atlas` for shared online persistence when needed

## Why This Stack

- `Python` is the right home for the engine, runners, adapters, metrics, and benchmark projects.
- `FastAPI` gives us a clean local API boundary for a control UI and future remote surfaces.
- `SQLite` is the right local database first: simple, file-based, portable, and sufficient for runs, jobs, adapter config, and metadata.
- `Next.js` plus `Mantine` is the right operator UI stack for a local admin surface and later hosted control plane.
- `SwiftUI` is the right native operator shell for local process supervision, status visibility, recovery actions, and future desktop automations.
- `Vercel` and `MongoDB Atlas` are for the optional online leg, not the local MVP core.

## Local-First MVP

The first working version should prove:

1. the platform contract
2. the engine-level runner
3. the git ratchet
4. the first agent adapter (`Mistral Vibe`)
5. one benchmark project

Do not block MVP delivery on:

- local open-source model support
- multiple agent adapters
- hosted control plane features

## Current Scaffold

The repository now includes:

- Python project metadata in `pyproject.toml`
- core package in `core/train_core/`
- local API package in `services/api/train_api/`
- native macOS shell scaffold in `apps/macos/`
- Alembic-backed local `SQLite` migrations
- run ledger and project-state foundation
- three reference benchmarks in `projects/`:
  - `mythology`
  - `helpdesk`
  - `reply`
- Vibe adapter contract in `.vibe/` and `scripts/run_vibe.py`
- autonomous guardrails for setup artifacts, dependency files, and budget bounds
- minimal `Next.js` + `Mantine` operator UI in `apps/web/`
- native SwiftUI operator shell in `apps/macos/`

Current endpoints:

- `GET /health`
- `GET /v1/agents`
- `GET /v1/agents/{agent_key}`
- `GET /v1/agents/{agent_key}/launch-plan`
- `GET /v1/providers`
- `GET /v1/providers/{provider_key}`
- `GET /v1/operator/status`
- `GET /v1/projects`
- `GET /v1/projects/templates`
- `GET /v1/projects/{project_key}`
- `GET /v1/project-states`
- `GET /v1/runs`
- `POST /v1/projects`
- `POST /v1/runs`
- `PUT /v1/projects/{project_key}`
- `POST /v1/runs/{run_id}/start`
- `POST /v1/runs/{run_id}/heartbeat`
- `POST /v1/runs/{run_id}/complete`
- `POST /v1/runs/{run_id}/execute`
- `POST /v1/runs/{run_id}/ratchet`
- `POST /v1/runs/{run_id}/resume`
- `DELETE /v1/projects/{project_key}`
- `GET /v1/runs/{run_id}`

Current engine contract:

- registered project definitions
- required bounded run budget
- machine-checkable autonomous guardrails
- formal DB migration startup on API boot
- explicit run lifecycle:
  - `pending`
  - `running`
  - terminal status via completion endpoint
- local run ledger in `SQLite`
- project state ledger with best-score tracking
- ratchet decision model
- git-state capture at ratchet time
- repo-local agent bootstrap contract for `Mistral Vibe`
- fail-closed setup/dependency/unauthorized-artifact enforcement before execution
- live provider registry and status probing for hosted and local backends
- durable operator status with heartbeat leases, stalled-run detection, and safe resume semantics
- managed project registry that overlays user-defined projects on top of built-in reference templates

Verified ratchet behavior:

- first successful run becomes the accepted baseline
- better runs are accepted and replace best-so-far
- worse runs are rejected and preserve the existing best score

Proof artifacts:

- `docs/PROOF_VIBE_CYCLE.md`
- `docs/SECOND_PROOF.md`
- `docs/PROOF_REPLY_CYCLE.md`

## Local Quickstart

```bash
uv sync
uv run uvicorn train_api.main:app --reload
```

Default local API URL:

- `http://127.0.0.1:8000`

Canonical Vibe planning launch:

```bash
uv run python scripts/run_vibe.py --project-key mythology --mode plan --print-only
```

Provider status check:

```bash
uv run python scripts/check_providers.py
```

Local operator UI:

```bash
cd apps/web
npm install
TRAIN_API_URL=http://127.0.0.1:8000 npm run dev
```

Native macOS shell:

```bash
cd apps/macos
swift build -c release
bash Scripts/build-bundle.sh
open dist/train.app
```

If the shell cannot find `uv`, set:

```bash
export TRAIN_UV_EXECUTABLE="$(command -v uv)"
```

Current native-shell scope:

- repo-root development shell today
- local engine supervision through `uv run uvicorn`
- Application Support state paths for logs, runtime metadata, and local shell DB
- attach to an already-healthy local engine on the preferred port when one is already running
- choose the next free local port when the preferred port is occupied by something else
- GitHub-release update checks
- dedicated Projects workspace with CRUD for managed projects and template-based bootstrapping from reference benchmarks

Not yet delivered in the native shell:

- managed Python runtime bootstrap for packaged installs
- in-app update download/install flow

## MVP Test

Current MVP smoke test:

```bash
uv sync
uv run python scripts/test_mvp.py
```

See [docs/MVP_TEST.md](./docs/MVP_TEST.md).

First autonomous proof artifact:

- [Vibe Proof Cycle](./docs/PROOF_VIBE_CYCLE.md)

Second platform-validation proof artifact:

- [Second Proof](./docs/SECOND_PROOF.md)

## Planned Repository Layout

```text
train/
  README.md
  docs/
    TECH_STACK.md
  core/
  scripts/
  services/
    api/
  apps/
    web/
  projects/
    mythology/
```

This layout now exists and is the active repository contract.

## Documentation

- [Contributing](./CONTRIBUTING.md)
- [Agents](./AGENTS.md)
- [Operating Model](./docs/OPERATING_MODEL.md)
- [Tech Stack](./docs/TECH_STACK.md)
- [Open Source Policy](./docs/OPEN_SOURCE.md)
- [Repository Contract](./docs/REPOSITORY_CONTRACT.md)
- [Setup](./docs/SETUP.md)
- [Environment](./docs/ENVIRONMENT.md)
- [MVP Test](./docs/MVP_TEST.md)
- [Vibe Proof Cycle](./docs/PROOF_VIBE_CYCLE.md)
- [Recovery](./docs/RECOVERY.md)
- [UI/UX Recovery](./docs/UI_UX_RECOVERY.md)
- [Status](./docs/STATUS.md)
- [Handover](./docs/HANDOVER.md)
- [Brain](./docs/BRAIN.md)
- [Skills](./docs/SKILLS.md)

## Current Roadmap Anchors

- GitHub issue `#1`: provider-neutral platform roadmap
- GitHub issue `#8`: cross-project guardrails and runtime bounds
- GitHub issue `#9`: hosted and local provider adapters
- GitHub issue `#10`: operator controls, watchdog recovery, and safe resume
