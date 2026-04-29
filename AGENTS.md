# AGENTS

## Purpose

This file is the fast-entry operating brief for coding agents working in this repository.

Read this before making changes.

## Project Identity

`autotrain` is a provider-neutral autonomous optimization platform.

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

- `ISSUE-4` runner and metric contract, unless `docs/STATUS.md` says otherwise

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
- future `Next.js` + `Mantine`

## Current State Summary

The repo already has:

- docs and operating model
- Python scaffold
- local API
- local run ledger
- registered benchmark project definition
- explicit run lifecycle endpoints

The repo does not yet have:

- actual benchmark execution runner
- ratchet logic
- provider adapters
- agent integration code

## Final Rule

Make the repository easier to resume than you found it.
