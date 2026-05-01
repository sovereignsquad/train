# Setup

## Purpose

This document defines the intended local setup path for contributors.

It describes the target environment the implementation should support.

## Local Development Targets

The local development environment should support:

- Python platform development
- local API development
- local benchmark execution
- optional local web UI development

## Required Base Tools

Expected local tools:

- `git`
- `Python 3.12+`
- `uv`
- `Swift 6+`
- Xcode Command Line Tools
- `Node.js` for the operator UI
- `npm`
- `vibe` via `uv tool install mistral-vibe`

## Planned Local Runtime

Core runtime:

- Python
- local filesystem
- local `SQLite`

Current scaffold:

- `uv`-managed Python environment
- `FastAPI` local API
- Alembic migration path initialized on API startup
- engine contract with project registry and run lifecycle endpoints
- real local mythology benchmark with deterministic prep and `val_bpb` scoring
- repo-local `Mistral Vibe` adapter contract in `.vibe/`
- provider registry with live Mistral and Ollama status probes
- operator heartbeat, stalled-run detection, and safe resume endpoints
- minimal `Next.js` + `Mantine` operator UI in `apps/web`
- native SwiftUI shell in `apps/macos`

Optional local integrations later:

- `Mistral Vibe`
- `Ollama`

## Environment Files

Use local environment files for development only.

Rules:

- never commit secrets
- keep local secrets in `.env`
- document expected variable names in `docs/ENVIRONMENT.md`

## Setup Strategy

The implementation phase should create a reproducible local setup with:

1. Python environment bootstrap
2. dependency installation
3. environment validation
4. Vibe bootstrap validation
5. provider connectivity validation
6. local DB initialization
7. local API startup
8. local benchmark run path
9. local UI startup
10. local macOS shell build

Current command sequence:

```bash
uv sync
uv run uvicorn train_api.main:app --reload
```

Vibe bootstrap:

```bash
uv tool install mistral-vibe
uv run python scripts/run_vibe.py --project-key mythology --mode plan --print-only
```

Local UI:

```bash
cd apps/web
npm install
TRAIN_API_URL=http://127.0.0.1:8000 npm run dev
```

Native shell:

```bash
cd apps/macos
swift build -c release
bash Scripts/build-bundle.sh
open dist/Train.app
```

If the native shell cannot resolve `uv` from its launch environment, set:

```bash
export TRAIN_UV_EXECUTABLE="$(command -v uv)"
```

MVP smoke test:

```bash
uv run python scripts/test_mvp.py
```

Provider connectivity check:

```bash
uv run python scripts/check_providers.py
```

## Planned Setup Scripts

Current scripts:

- `scripts/run_api.sh`
- `scripts/run_vibe.py`
- `scripts/check_providers.py`
- `scripts/test_mvp.py`
- `scripts/prove_vibe_cycle.py`
- `scripts/prove_second_project.py`
- `apps/macos/Scripts/build.sh`
- `apps/macos/Scripts/build-bundle.sh`

## Non-Goals

This setup should not initially require:

- hosted deployment
- MongoDB Atlas
- local open-source models
- multiple agent adapters

Those are later integrations, not prerequisites for local implementation.
