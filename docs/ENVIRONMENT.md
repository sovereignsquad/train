# Environment

## Purpose

This document defines the environment model for `train`.

Use only the environment names defined here.

## Environment Names

- `local`
- `staging`
- `production`

Do not invent ad hoc names in docs or issues.

## Local

Purpose:

- platform development
- benchmark development
- local testing
- local operator workflows

Expected characteristics:

- Python-first runtime
- local `SQLite`
- filesystem artifacts
- optional local web UI
- optional native macOS shell
- optional local agent/provider integrations

## Staging

Purpose:

- shared preview of the hosted leg
- deployment verification
- integration validation

Expected characteristics:

- likely Vercel-hosted web UI
- likely shared cloud persistence when needed

## Production

Purpose:

- real hosted operator/control-plane environment

Expected characteristics:

- Vercel-hosted web UI
- cloud persistence such as `MongoDB Atlas`
- documented secrets and deployment procedures

## Secret Policy

Rules:

- secrets never go into git
- `.env` is local-only
- hosted secrets belong in the deployment platform secret store
- every expected secret must be documented by name and purpose

## Environment Variable Documentation Rule

When a new variable is introduced, document:

- variable name
- environment(s) used
- whether required or optional
- purpose
- example shape, not the real secret

## Planned Variables

These are the current local variables:

- `MISTRAL_API_KEY`
- `MISTRAL_API_BASE_URL`
- `MISTRAL_VIBE_EXECUTABLE`
- `MISTRAL_VIBE_AGENT_NAME`
- `MISTRAL_VIBE_HOME`
- `OPERATOR_LEASE_GRACE_SECONDS`
- `OLLAMA_BASE_URL`
- `TRAIN_REPO_ROOT`
- `TRAIN_ROOT_DIR`
- `TRAIN_STATE_DIR`
- `TRAIN_UV_EXECUTABLE`
- `DATABASE_URL`
- `TRAIN_ENV`
- `APP_HOST`
- `APP_PORT`
- `TRAIN_API_URL`

### Variable Reference

`TRAIN_ENV`

- environments: `local`, later `staging` and `production`
- required: no
- default: `local`
- purpose: names the active runtime environment

`APP_HOST`

- environments: `local`
- required: no
- default: `127.0.0.1`
- purpose: local FastAPI bind host

`APP_PORT`

- environments: `local`
- required: no
- default: `8000`
- purpose: local FastAPI bind port

`DATABASE_URL`

- environments: `local`, later hosted environments
- required: no
- default: local `SQLite` path
- purpose: database connection string for platform state and metadata

`MISTRAL_API_KEY`

- environments: local or hosted when using Mistral-backed integrations
- required: required for real Mistral-backed provider checks and Vibe-backed agent runs
- default: none
- purpose: provider credential for Mistral-backed agent or model integrations

`MISTRAL_API_BASE_URL`

- environments: `local`, later hosted environments
- required: no
- default: `https://api.mistral.ai`
- purpose: overrides the hosted Mistral API base URL used by the provider adapter

`MISTRAL_VIBE_EXECUTABLE`

- environments: `local`
- required: no
- default: `vibe`
- purpose: overrides the executable path/name used by the first agent adapter

`MISTRAL_VIBE_AGENT_NAME`

- environments: `local`
- required: no
- default: `train`
- purpose: selects the repo-local Vibe agent profile under `.vibe/agents/`

`MISTRAL_VIBE_HOME`

- environments: `local`
- required: no
- default: `artifacts/local/vibe-home`
- purpose: isolates runtime Vibe metadata from the repo-tracked `.vibe/` contract

`OLLAMA_BASE_URL`

- environments: `local`
- required: no
- default: `http://127.0.0.1:11434`
- purpose: overrides the local Ollama API base URL used by the provider adapter

`OPERATOR_LEASE_GRACE_SECONDS`

- environments: `local`, later `staging` and `production`
- required: no
- default: `30`
- purpose: extends run lease expiry beyond the declared budget so stalled-run detection and resume semantics remain bounded

`TRAIN_REPO_ROOT`

- environments: local macOS shell development
- required: no
- default: none
- purpose: overrides repository-root discovery for the native macOS shell when launching the local engine

`TRAIN_ROOT_DIR`

- environments: local engine execution, especially native macOS shell launches
- required: no
- default: resolved source checkout root
- purpose: overrides the runtime root used by Python services, migrations, scripts, projects, and bundled runtime launches

`TRAIN_STATE_DIR`

- environments: local engine execution, especially native macOS shell launches
- required: no
- default: `<TRAIN_ROOT_DIR>/artifacts/local`
- purpose: overrides the writable state directory used for SQLite and other local runtime state

`TRAIN_UV_EXECUTABLE`

- environments: local macOS shell development
- required: no
- default: resolved from `PATH`, then common Homebrew/system locations
- purpose: overrides `uv` executable discovery for the native macOS shell when launching the local engine

`TRAIN_API_URL`

- environments: `local`, later `staging` and `production`
- required: no
- default: `http://127.0.0.1:8000`
- purpose: points the Next.js operator UI at the API base URL

## Environment Ownership

Platform code must not assume:

- hosted-only execution
- Atlas-first storage
- one specific agent adapter

The local environment is the default implementation target.
