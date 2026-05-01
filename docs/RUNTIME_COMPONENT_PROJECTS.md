# Runtime Component Projects

## Purpose

This document defines how `{train}` optimizes bounded components of external runtime systems.

## Core Rule

`{train}` may optimize runtime components.

`{train}` must not absorb runtime ownership.

That means:

- the runtime system stays outside `{train}` core
- the optimization target is copied or represented as a bounded project artifact
- the benchmark evaluates the component under explicit local rules

## Suitable Runtime Targets

Good targets:

- retrieval policy
- ranking policy
- generation policy
- refinement policy
- abstain or escalation policy
- deterministic scoring logic

Bad targets:

- the whole runtime orchestration layer
- mixed UI and runtime flows
- unconstrained data ingestion pipelines
- product-specific sync and delivery behavior

## Required Contract

A runtime component project still needs the normal `{train}` contract:

- one controlled mutable artifact
- one bounded run entrypoint
- one machine-readable score
- protected setup and dependency files

## Runtime Ownership Boundary

When the target lives inside another system such as `{trinity}`:

- `{trinity}` runs the brain
- `{train}` improves a bounded piece of the brain

Do not move runtime orchestration, product adapters, or delivery logic into `core/train_core/`.

## Benchmark Design Rules

The local benchmark should:

- isolate the component honestly
- use realistic but bounded fixtures or local data contracts
- emit a score that reflects the chosen component
- stay reproducible enough for keep-or-reject automation

## Delivery Rule

A runtime component project is complete only if another developer can answer:

1. what runtime component is being improved
2. where the mutable artifact lives
3. how the benchmark evaluates it
4. how the result maps back to the production runtime

