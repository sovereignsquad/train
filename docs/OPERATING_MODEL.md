# Operating Model

## Purpose

This document defines how `train` work is coordinated.

The goal is to make delivery strict, predictable, and low-ambiguity:

- one source of truth for each type of information
- one way to name and refer to work
- one execution path from idea to shipped result
- explicit gates for product, engineering, and operations work

This is the operating contract for humans and agents working on the repository.

## Core Principles

1. Delivery beats discussion.
2. Every decision must land in one durable source of truth.
3. No parallel shadow planning.
4. Requirements, implementation, and operations must be referable by stable IDs.
5. If something is not written in the agreed source, it is not authoritative.
6. DevOps and operational work follow the same rigor as product features.
7. All project documentation must be written as public open-source documentation.
8. Repository behavior must stay consistent with the `Apache-2.0` licensing posture.

## Communication Model

We communicate at four levels only:

### 1. Roadmap

Purpose:

- define what matters next
- sequence delivery
- decide what is in scope

System:

- GitHub Project board
- GitHub issues

Rule:

- roadmap decisions live in issues, not chat

### 2. Specifications

Purpose:

- define what a thing is
- define constraints, interfaces, and acceptance checks

System:

- repository docs under `docs/`

Rule:

- if a behavior or architecture matters to implementation, it must exist in repo docs

### 3. Execution

Purpose:

- implement the work
- review the work
- merge the work

System:

- branches
- commits
- pull requests

Rule:

- implementation discussion belongs in code, diffs, and PRs

### 4. Operations

Purpose:

- environment
- deployment
- secrets
- reliability
- recovery

System:

- repository docs
- environment templates
- deployment config
- runbooks

Rule:

- operational steps must be documented as procedures, not left as tribal knowledge

## SSOT Model

There is not one global SSOT file. There is one SSOT per information type.

That is the only scalable way to stay strict.

## SSOT By Domain

### Product / Delivery SSOT

- GitHub Project board
- GitHub issues

Authoritative for:

- priority
- sequencing
- scope
- acceptance criteria
- dependencies

If an issue conflicts with chat, the issue wins after it is updated.

### Architecture SSOT

- `docs/OPERATING_MODEL.md`
- `docs/ROUND_CONTRACT.md`
- `docs/TECH_STACK.md`
- `docs/OPEN_SOURCE.md`
- `docs/BRAIN.md`
- `docs/SKILLS.md`
- future architecture docs under `docs/`

Authoritative for:

- system boundaries
- round-based learning contract
- stack choices
- adapter boundaries
- repository contract
- operating rules
- open-source posture

### Code SSOT

- the repository itself

Authoritative for:

- actual implementation
- interfaces in use
- migrations
- scripts
- tests

### Operations SSOT

- future docs such as:
  - `docs/STATUS.md`
  - `docs/HANDOVER.md`
  - `docs/RUNBOOKS.md`
  - `docs/DEPLOYMENT.md`
  - `docs/SECRETS.md`
  - `docs/RECOVERY.md`

Authoritative for:

- environment setup
- deployment flow
- incident recovery
- operator procedures
- short-term current state
- resumable handoff context

## Reference Rules

We need stable references everywhere.

Use these forms only:

### Work Items

- `ISSUE-<number>`
- example: `ISSUE-9`

Meaning:

- GitHub issue number is the primary work reference

### Documents

- use repo path
- example: `docs/TECH_STACK.md`

### Components

- use domain-prefixed names
- examples:
  - `engine.runner`
  - `engine.ratchet`
  - `adapter.agent.vibe`
  - `adapter.provider.ollama`
  - `project.mythology`

### Decisions

When a decision matters, record it in docs with a decision heading:

- `DECISION: <short title>`

Example:

- `DECISION: SQLite is the default local database`

### Environments

Use fixed names only:

- `local`
- `staging`
- `production`

Do not invent ad hoc names in tickets or docs.

## Naming Rules

Keep naming rigid:

### Issues

Use:

- `{train}: <outcome>`

Examples:

- `{train}: Build the engine-level experiment runner and metric contract`
- `{train}: Add provider adapters for hosted and local model backends`

### Branches

Use:

- `issue-<number>-<slug>`

Examples:

- `issue-4-engine-runner`
- `issue-9-provider-adapters`

### Commits

Use:

- `<area>: <change>`

Examples:

- `engine: add bounded run result contract`
- `docs: define operating model`
- `api: add health and run endpoints`

### Pull Requests

Use:

- `[ISSUE-<number>] <title>`

Example:

- `[ISSUE-4] Add engine-level run result contract`

## How We Work

Every piece of work moves through the same path.

1. Define the issue.
2. Confirm SSOT docs if architecture or operations are affected.
3. Implement on an issue branch.
4. Verify against acceptance checks.
5. Update docs if behavior, operations, or interfaces changed.
6. Merge only when the issue and docs agree.

## Strict Delivery Rules

These rules are mandatory.

### Rule 1: No undocumented architecture drift

If the stack, boundaries, or operating model change:

- update the docs in the same workstream

### Rule 2: No silent operational knowledge

If something must be known to run, deploy, recover, or debug the system:

- it must be written in docs

### Rule 3: No vague done state

Every issue must include:

- explicit acceptance checks
- explicit dependencies
- explicit out-of-scope

### Rule 4: No mixed abstraction layers

Do not conflate:

- project logic
- engine logic
- agent adapters
- provider adapters
- deployment concerns

### Rule 5: No implementation before contract on core work

For work that affects:

- engine boundaries
- stack decisions
- environment model
- adapter interfaces

document the contract before or during implementation, not after.

### Rule 6: No operations as “later cleanup”

If a task creates new operational burden:

- secrets
- startup
- deployment
- restart
- failure recovery

it must create or update operational docs immediately.

### Rule 7: No private-only documentation habits

Because this is an open-source project:

- docs must be understandable without private chat context
- decisions must be written in public project language
- repository standards must be visible in-repo

## Focus Rules

Focus is protected by limiting simultaneous work.

### Active Work Limit

At most:

- 1 issue `In Progress (NOW)` for core platform work
- optionally 1 sidecar docs/ops task if it does not compete with the core path

Do not run multiple core implementation lanes unless the work is cleanly separable.

### Priority Order

Always prefer:

1. unblock the core path
2. prove the loop
3. harden the loop
4. expand adapters
5. expand domains

Never reverse this order without explicitly updating roadmap issues.

## DevOps Discipline

DevOps is not support work. It is product-critical work.

Operational tasks must be treated like features.

Each operational change should define:

- objective
- system touched
- environment touched
- rollback path
- verification steps
- failure modes

## Required Operational Documents

We should add these as the platform grows:

- `docs/SETUP.md`
- `docs/ENVIRONMENT.md`
- `docs/SECRETS.md`
- `docs/DEPLOYMENT.md`
- `docs/RUNBOOKS.md`
- `docs/RECOVERY.md`

## Change Control

Any change to these must update SSOT:

- stack
- environment model
- storage model
- adapter model
- deployment model
- operational procedures

Minimum required updates:

- relevant issue
- relevant doc
- implementation

If one of the three is missing, the work is incomplete.

## Decision Hierarchy

When sources disagree, resolve in this order:

1. updated repository docs
2. updated GitHub issue scope and acceptance checks
3. current implementation
4. chat discussion

Chat alone is never final authority.

## Definition Of Done

Work is done only when all are true:

- code is implemented
- acceptance checks pass
- docs are updated if needed
- operational impact is documented if needed
- issue status is updated

## Immediate Next Docs To Add

To make this operating model fully useful, the next documentation set should be:

1. `docs/ARCHITECTURE.md`
2. `docs/DEPLOYMENT.md`
3. `docs/RUNBOOKS.md`
4. `docs/RECOVERY.md`
5. `docs/SECRETS.md`
