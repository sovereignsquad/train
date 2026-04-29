# Skills

## Purpose

This document lists the recurring working patterns this repository needs.

It is not a platform feature list.

It is a human-and-agent execution catalog for repeatable work.

## Skill Categories

### 1. Platform Skills

These are repository-internal execution skills.

#### `skill.runner-contract`

Use when:

- defining run schemas
- defining lifecycle transitions
- defining project execution contracts

Expected outputs:

- schema changes
- API changes
- docs updates

#### `skill.ratchet-contract`

Use when:

- defining accept/reject semantics
- defining best-so-far comparison
- defining keep/revert logic

Expected outputs:

- core engine changes
- ledger changes
- issue/docs updates

#### `skill.project-contract`

Use when:

- adding or refining benchmark structure
- defining mutable artifact boundaries
- defining benchmark metadata

Expected outputs:

- `projects/<name>/` structure
- contract docs
- benchmark scaffolding

### 2. Operations Skills

#### `skill.local-setup`

Use when:

- bootstrapping local development
- validating environment assumptions
- updating setup docs

#### `skill.handover`

Use when:

- ending a work session
- switching agents
- resuming after interruption

Required updates:

- `docs/STATUS.md`
- `docs/HANDOVER.md`

### 3. Integration Skills

#### `skill.agent-adapter`

Use when:

- integrating `Mistral Vibe`
- later integrating `Cursor`
- defining agent-facing execution boundaries

#### `skill.provider-adapter`

Use when:

- integrating `Mistral API`
- integrating `Ollama`
- isolating provider-specific behavior

## How To Use This Catalog

When starting work:

1. identify which skill category applies
2. check the relevant SSOT docs
3. keep the change bounded to that skill domain
4. update handoff docs after meaningful progress

## Current Priority Skills

Current highest-priority skills:

1. `skill.runner-contract`
2. `skill.project-contract`
3. `skill.handover`

These matter most until the first real benchmark execution path exists.
