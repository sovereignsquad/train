# Brain

## Purpose

This document captures the durable mental model of the project.

It is not a changelog.
It is not a task list.

It is the long-term reasoning model for how the system is supposed to think.

## System Identity

`autotrain` is a platform for bounded autonomous optimization.

Its core loop is:

1. define a project contract
2. mutate one controlled artifact
3. run one bounded experiment
4. produce one automatic score
5. compare against prior state
6. keep or reject the change

Everything else is a supporting layer around that loop.

## Long-Term Invariants

These should remain true even as implementation evolves:

### Invariant 1

The platform is general-purpose.

The first benchmark teaches the platform; it does not define it.

### Invariant 2

Agent adapters and provider adapters are different things.

- agents drive code and workflows
- providers expose model backends

### Invariant 3

The local-first path is the primary implementation path.

Hosted infrastructure is additive.

### Invariant 4

The engine contract must be usable without committing to one benchmark, one agent, or one provider.

### Invariant 5

Open-source repository quality is part of the product, not documentation polish added later.

## Current Mental Model

Today the project is best understood as:

- a Python engine
- a local API shell
- a future operator UI
- one reference benchmark
- later adapters and hosted surfaces

## Architectural Direction

Near term:

- finish engine contract
- finish runner execution path
- add benchmark files
- add ratchet logic

Mid term:

- add agent integration boundary
- add provider integration boundary
- add operator visibility and recovery

Long term:

- validate with a second benchmark or second adapter surface

## Things To Resist

Resist these failure modes:

- turning `mythology` into platform code
- turning `Mistral Vibe` into platform code
- making local open-source models a prerequisite too early
- building UI before the core execution loop is real

## Decision Lens

When unsure, ask:

1. does this strengthen the core loop?
2. does this preserve the platform boundaries?
3. does this make future handoff easier?
4. does this help prove the MVP sooner?

If not, it is probably not the next move.
