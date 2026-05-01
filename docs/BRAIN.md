# Brain

## Purpose

This document captures the durable mental model of the project.

It is not a changelog.
It is not a task list.

It is the long-term reasoning model for how the system is supposed to think.

## System Identity

`{train}` is a platform for bounded autonomous optimization.

Its core loop is:

1. define a project contract
2. mutate one controlled artifact
3. run one bounded experiment
4. produce one automatic score
5. compare against prior state
6. keep or reject the change

Everything else is a supporting layer around that loop.

In the current multi-repo direction:

- `{trinity}` is the runtime workflow that runs brains
- `{train}` is the optimizer that improves brains

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

### Invariant 6

`{train}` must stay usable for optimizing external runtime systems without absorbing those runtime systems into its own core.

## Current Mental Model

Today the project is best understood as:

- a Python engine
- a local API shell
- a native and web operator surface
- a bounded-project optimizer
- reference benchmarks that prove the loop
- a future optimizer seam for external runtimes such as `{trinity}`

## Architectural Direction

Near term:

- finish native runtime bootstrap and packaged desktop delivery
- add managed-project bootstrap generation
- define how raw ideas become reusable project contracts
- prepare the first `{reply}`-style project template

Mid term:

- optimize bounded runtime components from external systems such as `{trinity}`
- add richer project templates beyond fixed reference benchmarks
- strengthen unattended operator and recovery paths

Long term:

- validate the platform across multiple brains, domains, and runtime systems

## Things To Resist

Resist these failure modes:

- turning `mythology` into platform code
- turning `Mistral Vibe` into platform code
- turning `{trinity}` runtime concerns into `{train}` engine code
- making local open-source models a prerequisite too early
- building UI before the core execution loop is real

## Decision Lens

When unsure, ask:

1. does this strengthen the core loop?
2. does this preserve the platform boundaries?
3. does this make future handoff easier?
4. does this help prove the MVP sooner?

If not, it is probably not the next move.
