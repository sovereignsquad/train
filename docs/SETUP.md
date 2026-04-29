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
- `Node.js` for the future web app
- `npm` or compatible package manager for the future web app

## Planned Local Runtime

Core runtime:

- Python
- local filesystem
- local `SQLite`

Current scaffold:

- `uv`-managed Python environment
- `FastAPI` local API
- `SQLite` database initialized on API startup
- engine contract with project registry and run lifecycle endpoints
- real local mythology benchmark with deterministic prep and `val_bpb` scoring

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
4. local DB initialization
5. local API startup
6. local benchmark run path

Current command sequence:

```bash
uv sync
uv run uvicorn autotrain_api.main:app --reload
```

MVP smoke test:

```bash
uv run python scripts/test_mvp.py
```

## Planned Setup Scripts

Expected script responsibilities:

- `scripts/check_env.*`
- `scripts/bootstrap.*`
- `scripts/run_api.*`
- `scripts/run_project.*`

Exact filenames may change, but setup should be scriptable and documented.

Current script:

- `scripts/run_api.sh`

## Non-Goals

This setup should not initially require:

- hosted deployment
- MongoDB Atlas
- local open-source models
- multiple agent adapters

Those are later integrations, not prerequisites for local implementation.
