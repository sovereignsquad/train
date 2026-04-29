# Tech Stack

## Decision Summary

`autotrain` is a Python-first platform with a local-first runtime and an optional hosted control plane.

The stack and architecture should be implemented in an open-source-friendly way under `Apache-2.0`, with clean boundaries between reusable platform logic and optional integrations.

The chosen stack is:

- Core engine: `Python 3.12+`
- API layer: `FastAPI`
- Validation and settings: `Pydantic`
- Dependency management: `uv`
- Local DB: `SQLite`
- Local artifact storage: filesystem
- Web UI: `Next.js`
- UI library: `Mantine`
- Hosted web deployment: `Vercel`
- Hosted shared DB: `MongoDB Atlas`
- First agent adapter: `Mistral Vibe`
- First hosted provider path: `Mistral API`
- First local provider path: `Ollama`

## Architecture Boundaries

Three boundaries matter:

### 1. Engine vs Project

The engine owns:

- bounded execution
- scoring
- keep/revert
- ledgering
- recovery

Projects own:

- setup logic
- controlled mutable artifact
- benchmark-specific metric implementation
- benchmark-specific assets and artifacts

### 2. Agent vs Provider

These must stay separate.

Agent adapters:

- edit code
- run shell commands
- interpret `program.md`
- drive the experiment workflow

Examples:

- `Mistral Vibe`
- future `Cursor`

Provider adapters:

- expose model inference backends when required
- unify hosted and local model access

Examples:

- `Mistral API`
- `Ollama`

### 3. Local vs Hosted

Local MVP:

- Python engine
- local API
- SQLite
- filesystem artifacts
- local UI

Hosted leg:

- Vercel-hosted UI
- optional shared API surface
- MongoDB Atlas-backed shared state

## Why Python

Python is the right fit for:

- runners
- experiment orchestration
- scoring
- benchmark ports
- CLI tooling
- adapter interfaces

It also aligns well with the first mythology benchmark and future research-style projects.

## Why FastAPI

FastAPI gives us:

- a clean local API boundary
- typed request/response models
- easy operator/control-plane endpoints
- good fit with Python services and async I/O when needed

## Why SQLite First

SQLite is the right local DB first because it is:

- file-based
- easy to inspect
- easy to back up
- enough for runs, jobs, status, settings, and metadata

Do not start with Mongo locally unless the platform proves a real need for it.

## Why Filesystem Artifacts

Artifacts such as:

- logs
- samples
- run outputs
- benchmark outputs

should live on disk first.

The DB should store metadata and references, not large blobs by default.

## Why Next.js + Mantine

The UI should be:

- easy to run locally
- strong for internal tools
- compatible with later hosted deployment

`Next.js` gives the right app shell for a future web control plane.

`Mantine` gives:

- strong app-shell components
- form primitives
- tables, overlays, notifications
- a solid fit for operator tooling

## Why Vercel + MongoDB Atlas Later

The hosted leg is optional for the MVP.

Use it when we need:

- team access
- shared run history
- remote operator controls
- public or semi-public control plane surfaces

At that point:

- deploy the web UI on `Vercel`
- store shared online state in `MongoDB Atlas`

## MVP Build Order

1. Define repository and project contract.
2. Build engine-level runner and metric contract.
3. Build ratchet and ledger.
4. Add `Mistral Vibe` as first agent adapter.
5. Add first mythology benchmark project.
6. Prove one full local benchmark loop.
7. Add provider-adapter layer.
8. Add second benchmark or second adapter surface.

## Current Implementation Baseline

The current implementation baseline includes:

- Python packaging via `uv`
- `FastAPI` local API
- `SQLite`-backed run ledger
- project registry for benchmark definitions
- run lifecycle API for create, start, and complete transitions

This is the first real engine contract layer. It is not yet the full benchmark execution runner or ratchet loop.

## Explicit Non-Goals For MVP

Do not require:

- local open-source models on day one
- multiple IDE/agent adapters
- hosted deployment before the local loop works
- MongoDB as the local default DB

## Open Questions

- Do we want `SQLAlchemy` or `SQLModel` for persistence?
- Do we want the local API and web UI in one repo from day one, or scaffold the web app after the engine contract stabilizes?
- Do we want the provider-adapter API in the MVP even if only one provider path is initially active?
