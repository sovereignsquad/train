# Autotrain

`autotrain` is a provider-neutral autonomous optimization platform.

The system is inspired by the `autoresearch` pattern:

- one controlled mutable artifact
- one automatic score
- one bounded experiment loop
- one ratchet that keeps improvements and reverts regressions

The first reference benchmark will use mythology / folktales training to prove the loop, but the platform is intended to support other optimization domains later.

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

### Agent Adapters

Agent adapters drive code-editing and execution workflows.

Planned:

- `Mistral Vibe` as the first agent adapter
- later additional agent adapters such as `Cursor`

### Provider Adapters

Provider adapters expose model backends to the platform when needed.

Planned:

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

### Hosted / Online Leg

- `Vercel` for the web surface
- `MongoDB Atlas` for shared online persistence when needed

## Why This Stack

- `Python` is the right home for the engine, runners, adapters, metrics, and benchmark projects.
- `FastAPI` gives us a clean local API boundary for a control UI and future remote surfaces.
- `SQLite` is the right local database first: simple, file-based, portable, and sufficient for runs, jobs, adapter config, and metadata.
- `Next.js` plus `Mantine` is the right operator UI stack for a local admin surface and later hosted control plane.
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
- core package in `core/autotrain_core/`
- local API package in `services/api/autotrain_api/`
- local `SQLite` foundation
- run ledger and project-state foundation

Current endpoints:

- `GET /health`
- `GET /v1/projects`
- `GET /v1/project-states`
- `GET /v1/runs`
- `POST /v1/runs`
- `POST /v1/runs/{run_id}/start`
- `POST /v1/runs/{run_id}/complete`
- `POST /v1/runs/{run_id}/execute`
- `POST /v1/runs/{run_id}/ratchet`
- `GET /v1/runs/{run_id}`

Current engine contract:

- registered project definitions
- required bounded run budget
- explicit run lifecycle:
  - `pending`
  - `running`
  - terminal status via completion endpoint
- local run ledger in `SQLite`
- project state ledger with best-score tracking
- ratchet decision model
- git-state capture at ratchet time

Verified ratchet behavior:

- first successful run becomes the accepted baseline
- better runs are accepted and replace best-so-far
- worse runs are rejected and preserve the existing best score

## Local Quickstart

```bash
uv sync
uv run uvicorn autotrain_api.main:app --reload
```

Default local API URL:

- `http://127.0.0.1:8000`

## MVP Test

Current MVP smoke test:

```bash
uv sync
uv run python scripts/test_mvp.py
```

See [docs/MVP_TEST.md](./docs/MVP_TEST.md).

## Planned Repository Layout

```text
autotrain/
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

This layout is a target contract, not the current completed state.

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
- [Recovery](./docs/RECOVERY.md)
- [Status](./docs/STATUS.md)
- [Handover](./docs/HANDOVER.md)
- [Brain](./docs/BRAIN.md)
- [Skills](./docs/SKILLS.md)

## Current Roadmap Anchors

- GitHub issue `#1`: provider-neutral platform roadmap
- GitHub issue `#3`: first agent adapter via Mistral Vibe
- GitHub issue `#5`: ratchet and experiment ledger
- GitHub issue `#9`: hosted and local provider adapters
