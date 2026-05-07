# Ecosystem Positioning

## Purpose

This document explains how `{train}` relates to nearby open-source ecosystems and what lessons it should borrow without losing its identity.

## Short Version

`{train}` should:

- borrow evaluation rigor
- borrow optimization framing
- avoid drifting into "yet another prompt framework"

## Useful Adjacent Categories

There are several open-source categories that are relevant to `{train}`.

### 1. Optimization Frameworks

Examples:

- `DSPy`
- `TextGrad`
- `AdalFlow`

Useful lesson:

- treat LLM behavior or policy behavior as something that can be improved systematically rather than tuned informally

What not to copy:

- framework identity centered on prompt graphs alone
- assumption that the optimized object is always a prompt or few-shot set

### 2. Evaluation Runners

Examples:

- `Promptfoo`
- `OpenAI Evals`

Useful lesson:

- fixed corpora
- same-input comparisons
- side-by-side reporting
- test-driven evidence culture

What not to copy:

- reducing the whole platform to an eval runner
- treating reporting as the product instead of bounded optimization

### 3. Lightweight Prompt/Function Toolkits

Examples:

- `ell`
- `Mirascope`

Useful lesson:

- keep behavior slices inspectable
- keep abstractions narrow and readable

What not to copy:

- framing `{train}` as a function-wrapper or prompt-versioning product

## What `{train}` Actually Is

`{train}` is not best understood as:

- a prompt IDE
- a prompt registry
- a model playground
- a thin eval CLI

`{train}` is best understood as:

- a bounded optimizer
- a replay-based offline teacher for external runtimes such as `{trinity}`
- a system with project contracts, artifact protection, and keep-or-reject governance

## Differentiators To Preserve

These are the characteristics that should stay true:

1. bounded project contracts
2. protected setup and dependency surfaces
3. explicit mutable-artifact ownership
4. replayable offline evaluation
5. proposal generation without runtime takeover
6. explicit promotion back into runtime-owned systems
7. optimizer governance instead of runtime ownership

If a future change weakens those, `{train}` is drifting.

## Borrowed Lessons

The right lessons to import are:

### Evaluation Rigor

- same inputs
- same budget
- explicit baseline/incumbent/candidate comparisons
- direct deltas
- machine-readable reports

### Optimization Framing

- make the improvement target explicit
- treat the behavior slice as a bounded learnable object
- improve through repeatable rounds rather than ad hoc edits

### Honest Reporting

- avoid speculative confidence
- preserve skeptical interpretation
- keep failure meaning explicit

## Failure Modes To Resist

Resist these forms of drift:

1. turning `{train}` into a prompt-abstraction library
2. turning `{train}` into a benchmark-reporting product only
3. turning `{train}` into a live runtime for `{reply}` or `{trinity}`
4. treating every behavior problem as prompt optimization
5. weakening project contracts in order to look more flexible

## Decision Rule

When evaluating a feature inspired by another project, ask:

1. does it strengthen bounded optimization?
2. does it improve evidence quality?
3. does it preserve runtime ownership outside `{train}`?
4. does it keep artifact and dependency governance explicit?

If not, it is probably ecosystem drift rather than platform progress.
