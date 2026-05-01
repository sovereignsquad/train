# Tech Stack

## Decision Summary

`train` is a Python-first platform with a local-first runtime and an optional hosted control plane.

The stack and architecture should be implemented in an open-source-friendly way under `Apache-2.0`, with clean boundaries between reusable platform logic and optional integrations.

The chosen stack is:

- Core engine: `Python 3.12+`
- API layer: `FastAPI`
- Native desktop shell: `Swift 6` + `SwiftUI`
- Validation and settings: `Pydantic`
- Dependency management: `uv`
- DB migrations: `Alembic`
- Local DB: `SQLite`
- Local artifact storage: filesystem
- Web UI: `Next.js`
- UI library: `Mantine`
- Native desktop packaging: `Swift Package Manager`
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

### 4. Native Shell vs Engine

The native macOS app owns:

- process supervision
- native operator UI
- update UX
- future automation hooks

The Python engine owns:

- benchmark execution
- ratchet logic
- providers
- agents
- project state

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
- Alembic-backed startup migrations
- `SQLite`-backed run ledger
- project registry for benchmark definitions
- real mythology benchmark scoring path
- second helpdesk benchmark scoring path with a maximize-metric classifier
- `Mistral Vibe` adapter status and launch-plan surfaces
- provider adapter registry and live status probes for:
  - `Mistral API`
  - `Ollama`
- operator status and recovery layer with:
  - heartbeat leases
  - stalled-run detection
  - safe resume semantics
- native macOS shell scaffold with:
  - SwiftPM app target
  - local engine supervisor
  - API-backed operator dashboard
  - release-check scaffold
- machine-checkable autonomous guardrails for mutable artifacts, setup artifacts, dependency artifacts, and budget bounds
- `Next.js` + `Mantine` operator UI for health, providers, projects, runs, project states, and recovery actions

This is now a two-project local baseline with a native shell scaffold. The next lane is runtime bootstrap and packaged desktop delivery, not basic project reuse.

## Explicit Non-Goals For MVP

Do not require:

- local open-source models on day one
- multiple IDE/agent adapters
- hosted deployment before the local loop works
- MongoDB as the local default DB

## Current Gaps

- ratchet mutation still assumes a single declared mutable artifact
- operator recovery is intentionally narrow and currently covers resume-from-checkpoint, not full workflow orchestration
- native app runtime bootstrap and packaged engine delivery are not implemented yet
