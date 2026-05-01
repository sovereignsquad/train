# TRAIN OVERVIEW

## Purpose

This document explains what `{train}` is, how it works, what it is capable of, and what it is not.

It is a durable high-level overview for:

- founders
- developers
- operators
- future coding agents

## What `{train}` Is

`{train}` is a provider-neutral autonomous optimization platform.

Its role is to improve bounded components through explicit experiments, automatic scoring, and keep-or-reject ratcheting.

In the current multi-repo architecture:

- `{reply}` is the product
- `{trinity}` runs brains
- `{train}` improves brains

That distinction matters.

`{train}` is not the live product runtime and it is not the omnichannel messaging product.

## Core Idea

`{train}` exists to run a strict loop:

1. define a project contract
2. mutate a controlled artifact
3. run a bounded experiment
4. produce an automatic score
5. compare against prior best state
6. keep or reject the change

That is the heart of the platform.

Everything else exists to support that loop safely and repeatably.

## What Problem `{train}` Solves

`{train}` solves the problem of improving a system component without turning the whole system into an uncontrolled experiment.

It is designed for situations where you want:

- one declared thing to improve
- one measurable outcome
- one bounded execution path
- one reversible decision

Instead of changing a whole product at once, `{train}` improves one explicit component at a time.

## Architectural Position

The current intended relationship is:

- `{reply}` owns contacts, channels, timelines, composer behavior, and user actions
- `{trinity}` owns evidence ingestion, candidate generation, refinement, evaluation, ranking, and feedback runtime logic
- `{train}` owns optimization, scoring, proof, ratchet, and controlled improvement of bounded components

This means:

- live drafting belongs in `{reply}` and `{trinity}`
- offline optimization belongs in `{train}`

## Platform Shape

The platform is split into four core layers:

1. experiment engine
2. project contract
3. agent adapters
4. provider adapters

These layers must stay separate.

### Experiment Engine

The engine owns:

- run budget enforcement
- execution lifecycle
- metric parsing
- result records
- best-so-far comparison
- ratchet keep/reject logic
- recovery boundaries

### Project Contract

A `{train}` project defines:

- one primary mutable artifact
- allowed autonomous mutable artifacts
- setup artifacts
- dependency artifacts
- one bounded run entrypoint
- one automatic metric
- budget bounds
- project-local files and assets

Projects may represent:

- a standalone benchmark
- a bounded runtime component from another system such as `{trinity}`

### Agent Adapters

Agent adapters drive code-editing and experiment workflows.

Delivered first adapter:

- `Mistral Vibe`

Planned later:

- additional adapters such as `Cursor`

### Provider Adapters

Provider adapters expose model backends when a workflow needs them.

Delivered provider paths:

- `Mistral API`
- `Ollama`

## How `{train}` Works

At runtime, the system works like this:

1. a project definition is selected
2. a run is created with a bounded budget
3. the benchmark entrypoint is executed
4. the run returns a structured result with a metric
5. the metric is compared against the project’s current best state
6. the ratchet either accepts or rejects the candidate
7. accepted changes are committed
8. rejected changes are restored

The behavior is deliberately strict and local-first.

## Run Lifecycle

The current lifecycle model includes:

- `pending`
- `running`
- terminal completion
- ratchet evaluation
- accepted or rejected terminal state
- optional resume lineage after failure or stall

This is backed by a local ledger and project state tracking.

## Guardrails

`{train}` is designed to fail closed.

The current guardrails enforce:

- mutable artifact restrictions
- setup artifact protection
- dependency artifact protection
- project budget bounds
- unauthorized file mutation blocking

The ratchet now supports multiple declared mutable artifacts, but only when those paths are explicitly allowed in the project contract.

It does not widen mutation scope just because files are dirty.

## Ratchet Model

The ratchet is the acceptance layer.

Current ratchet behavior:

- the first successful run becomes the baseline
- a better result is accepted
- a worse result is rejected
- accepted runs commit changed allowed mutable artifacts
- rejected runs restore changed allowed mutable artifacts
- unauthorized or protected-path changes are blocked

This gives the platform a reversible, inspectable improvement path.

## Recovery Model

`{train}` already includes a narrow but real recovery baseline:

- heartbeat leases
- stalled-run detection
- operator visibility into recoverable runs
- safe resume from known-good checkpoint state

This is not full workflow orchestration, but it is a real operator safety layer.

## Current Built-In Projects

The repository currently includes three reference projects:

### `project.mythology`

Purpose:

- the original reference benchmark used to prove the platform loop

Shape:

- benchmark-style project
- `minimize` metric

### `project.helpdesk`

Purpose:

- second reference benchmark proving the engine works beyond the first project shape

Shape:

- deterministic intent-classification project
- `maximize` metric

### `project.reply`

Purpose:

- starter Trinity-style reply benchmark

Shape:

- deterministic local reply-drafting project
- `maximize` metric
- local-only data override support

This is a seam proof project, not yet a production `{reply}` integration.

## Current Operator Surfaces

`{train}` already has two operator surfaces.

### Local API

The local Python API exposes:

- health
- project registry
- managed projects
- runs
- ratchet actions
- operator status
- provider status
- agent status
- resume and recovery controls

### Native macOS Shell

The macOS app currently provides:

- local engine supervision
- API-backed dashboard
- managed project workspace
- recovery visibility and actions
- packaged runtime bootstrap
- bundled runtime template
- native toolbar-driven operator controls

There is also a web operator UI built with `Next.js` and `Mantine`.

## Managed Projects

`{train}` is not limited to built-in reference benchmarks.

It already supports:

- reference templates
- user-defined managed projects
- CRUD operations for managed projects
- starter project bootstrap generation

This means new bounded optimization projects can be created without hardcoding everything into platform core.

## What `{train}` Can Already Do

Today `{train}` can:

- run bounded benchmark projects
- enforce project budgets
- track run history in `SQLite`
- track best-so-far metrics per project
- accept or reject candidate improvements automatically
- commit or restore mutable artifacts through git
- block unauthorized changes
- expose agent/provider/operator status over API
- bootstrap starter project workspaces
- supervise the engine through a native macOS app
- prove improvement loops through repeatable proof scripts
- optimize bounded components of external runtime systems, as shown by the starter `{reply}` proof

## What `{train}` Is Capable Of Conceptually

`{train}` is designed to optimize:

- benchmark code
- scoring logic
- retrieval policy
- ranking policy
- prompt policy
- bounded runtime components from external systems such as `{trinity}`

It is suitable for:

- deterministic local experiments
- repeated keep-or-reject optimization
- improving one component of a larger system without absorbing the full system into platform core

## What `{train}` Is Not

`{train}` is not:

- the omnichannel messaging product
- the live candidate-processing runtime
- a general workflow engine
- a full model-training platform in the foundation-model sense
- a substitute for `{reply}`
- a substitute for `{trinity}`

If the work is:

- product and user interaction behavior, it belongs in `{reply}`
- live runtime workflow behavior, it belongs in `{trinity}`
- bounded improvement of a declared artifact with a score, it belongs in `{train}`

## Current Technical Stack

The current stack is:

- `Python`
- `FastAPI`
- `Pydantic`
- `uv`
- `Alembic`
- `SQLite`
- `Next.js`
- `Mantine`
- `Swift`
- `SwiftUI`
- `SwiftPM`

Current model-facing integrations:

- `Mistral Vibe`
- `Mistral API`
- `Ollama`

## What Has Already Been Proven

The repository has already proven:

- one real agent-driven optimization cycle
- reuse across more than one benchmark project
- support for both `minimize` and `maximize` metrics
- safe ratchet semantics with keep/reject behavior
- protected-path guardrails
- Trinity-style bounded runtime component optimization through the starter `{reply}` proof
- multi-artifact git mutation support inside declared mutable artifact sets

This means `{train}` is already beyond a conceptual prototype.

## Current Limits

Important current limits:

- real private `{reply}` data integration is not implemented yet
- packaged desktop update installation is not implemented yet
- unattended long-running heartbeat exercise is not fully proven yet
- the starter `{reply}` benchmark is still deterministic and simplified
- `Vibe` turn-limit exit behavior still deserves follow-up hardening

## Best Short Definition

`{train}` is a local-first optimization platform that improves bounded code or runtime components through controlled mutation, automatic scoring, and git-backed keep-or-reject ratcheting.

## Practical Reading Order

If you are new to the repository, read in this order:

1. `README.md`
2. `docs/OPERATING_MODEL.md`
3. `docs/TECH_STACK.md`
4. `docs/REPOSITORY_CONTRACT.md`
5. `docs/BRAIN.md`
6. `docs/STATUS.md`
7. `docs/HANDOVER.md`

## Final Rule

The most important boundary to preserve is:

- `{reply}` uses brains
- `{trinity}` runs brains
- `{train}` improves brains

If a change weakens that boundary, it is probably the wrong change.
