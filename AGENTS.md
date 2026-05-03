# AGENTS

## Purpose

This file is the fast-entry operating brief for coding agents working in this repository.

Read this before making changes.

## Project Identity

`{train}` is a provider-neutral autonomous optimization platform.

It is not:

- a single benchmark project
- a single vendor integration
- a single IDE workflow

The first benchmark is `project.mythology`.

## Core Boundaries

Keep these layers separate:

1. `engine.*`
2. `project.*`
3. `adapter.agent.*`
4. `adapter.provider.*`
5. `ops.*`

Do not collapse them into one implementation layer.

## Primary SSOT

Before changing code, read:

- `README.md`
- `docs/OPERATING_MODEL.md`
- `docs/TECH_STACK.md`
- `docs/REPOSITORY_CONTRACT.md`
- `docs/STATUS.md`
- `docs/HANDOVER.md`
- `docs/BRAIN.md`
- `docs/SKILLS.md`

## Active Delivery Focus

Current active implementation lane:

- `docs/STATUS.md` is authoritative; current next lane is native runtime bootstrap and packaged desktop delivery unless it says otherwise

Always check `docs/STATUS.md` before starting.

## Required Work Pattern

1. Confirm active issue and acceptance checks.
2. Read the relevant SSOT docs.
3. Implement the smallest correct step on the critical path.
4. Update docs if architecture, setup, operations, or status changed.
5. Leave the repo in a resumable state.

## Documentation Rule

If you learn something future contributors or agents need:

- write it into the repo

Do not leave critical context in chat only.

## Native App UI Rule

When touching `apps/web` or `apps/macos`, preserve the native-app standard:

- `{train}` is a native app, not a website
- the primary macOS workspace must be pure SwiftUI/AppKit
- do not move core operator flows back into HTML/CSS/JavaScript shells
- do not introduce website-style UX metaphors into shipped operator flows
- keep core actions in shell chrome, panels, or dialogs
- require all shipped visual assets and iconography to be locally available offline
- use one consistent local icon system and one shared icon sizing contract
- prefer explicit visual rendering contracts over heuristic markup/path guessing
- keep native app icon generation deterministic and local-only; do not rely on Quick Look, browser capture, or heuristic raster paths
- verify bundle icon metadata and refresh macOS app registration after native app installs

## Memory Rule

When significant work completes, update:

- `docs/STATUS.md`
- `docs/HANDOVER.md`

If you do not update those, the work is not properly handed over.

## Implementation Bias

Bias toward:

- explicit contracts
- narrow, testable increments
- local-first implementation
- deterministic behavior

Avoid:

- premature abstraction
- speculative integrations
- benchmark-specific assumptions in platform code

## Current Stack

- `Python`
- `FastAPI`
- `SQLite`
- `uv`
- `Next.js`
- `Mantine`
- `Swift`
- `SwiftUI`

## Current State Summary

The repo already has:

- docs and operating model
- Python scaffold
- local API
- local run ledger
- registered benchmark project definition
- explicit run lifecycle endpoints
- real benchmark execution runner
- ratchet logic
- `Mistral Vibe` agent integration
- provider adapters for `Mistral API` and `Ollama`
- minimal operator UI
- native macOS shell scaffold

## Final Rule

Make the repository easier to resume than you found it.
