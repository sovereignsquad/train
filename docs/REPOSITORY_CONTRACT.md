# Repository Contract

## Purpose

This document defines the intended structure of the `autotrain` repository.

It is the contract contributors and agents must follow when adding code.

## Core Separation

The repository is divided into five concerns:

1. docs
2. platform core
3. API/service layer
4. web/operator UI
5. projects/benchmarks

These concerns must not be mixed casually.

## Intended Layout

```text
autotrain/
  README.md
  LICENSE
  CONTRIBUTING.md
  docs/
    OPERATING_MODEL.md
    OPEN_SOURCE.md
    TECH_STACK.md
    REPOSITORY_CONTRACT.md
    SETUP.md
    ENVIRONMENT.md
  core/
    engine/
    adapters/
    storage/
    schemas/
  services/
    api/
  apps/
    web/
  scripts/
  projects/
    mythology/
```

## Directory Responsibilities

### `docs/`

Holds SSOT project documentation.

Do not hide important architecture or operational knowledge outside this directory.

### `core/`

Holds reusable platform code.

Includes:

- experiment engine
- ratchet logic
- adapter interfaces and implementations
- storage abstractions
- shared schemas

Do not put benchmark-specific logic here unless it is truly reusable.

### `services/api/`

Holds the local Python API surface.

This layer should expose:

- health endpoints
- run control
- status
- logs/metadata access

This layer should not contain engine internals that belong in `core/`.

### `apps/web/`

Holds the operator UI.

Expected stack:

- `Next.js`
- `Mantine`

This layer should consume API contracts, not re-implement engine behavior.

### `scripts/`

Holds operational scripts and bootstrap helpers.

Use for:

- local setup helpers
- dev bootstrap
- environment validation
- execution wrappers

Do not bury business logic here if it belongs in Python modules.

### `projects/`

Holds concrete benchmark or domain projects.

Each project should fit the platform contract and remain isolated from other projects.

## Project Contract

Each project should provide:

- one setup artifact or setup entrypoint
- one controlled mutable artifact
- `program.md`
- one bounded run entrypoint
- one automatic metric
- logs and artifacts

The exact file names may vary by project type, but the contract must remain explicit.

Current registered benchmark:

- `project_key = mythology`
- mutable artifact target: `projects/mythology/train.py`
- default metric: `val_bpb`

## Boundary Rules

### Engine vs Project

Engine code belongs in `core/`.

Project-specific benchmark logic belongs in `projects/<name>/`.

### Agent vs Provider

Agent adapters belong under `core/adapters/agent/`.

Provider adapters belong under `core/adapters/provider/`.

Do not combine them into one adapter layer.

### Local vs Hosted

Local-first support is mandatory.

Hosted support is optional and should layer on top cleanly.

## Persistence Contract

Local default:

- `SQLite` for state and metadata
- filesystem for artifacts

Cloud later:

- hosted persistence may use `MongoDB Atlas`

Do not design the local core around Atlas-first assumptions.

## Documentation Contract

When the repository contract changes:

- update this file
- update related docs
- update the issue that drove the change

If code and this contract disagree, the mismatch must be resolved immediately.
