# Hypothesis Contract

## Purpose

This document defines the `hypothesis.md` contract for serious `{train}` projects.

Use it when a project is intended to produce durable learning rather than a one-off smoke proof.

## Why This Exists

`{train}` already knows how to:

- mutate a bounded artifact
- run a benchmark
- score the result
- ratchet accepted improvements

That is not enough on its own.

Without an explicit hypothesis artifact:

- projects drift into metric-chasing
- future contributors cannot tell what mechanism was being tested
- failure becomes hard to interpret honestly
- round reports become harder to trust

`hypothesis.md` fixes that by making the learning claim public and durable.

## When It Is Required

`hypothesis.md` is required for serious projects.

In this repository, that means:

- all reference projects intended for repeated optimization
- all managed projects created through the normal project contract
- all external-runtime component projects such as `{trinity}` slices
- all future OpenMythos-like external research-system projects

It is not required for:

- trivial scratch fixtures
- one-off local throwaway experiments that are not part of the project registry

## File Location

The file must live in the project directory beside `program.md`.

Examples:

- `projects/reply/hypothesis.md`
- `projects/trinity_frontier/hypothesis.md`
- `projects/mythology/hypothesis.md`

## Minimum Required Content

Each `hypothesis.md` must state:

1. component under optimization
2. expected improvement
3. reason for that expectation
4. metric expected to move
5. what failure would mean

The goal is not long-form writing.
The goal is honest, inspectable project reasoning.

## Recommended Shape

Use these sections:

- `Component Under Optimization`
- `Hypothesis`
- `Expected Metric Movement`
- `Failure Meaning`

Optional sections:

- `Known Confounds`
- `Out Of Scope`
- `Next Round Trigger`

## Quality Bar

Good hypothesis docs are:

- concise
- specific
- falsifiable
- aligned to the declared mutable artifact
- aligned to the declared metric

Bad hypothesis docs are:

- generic aspirations
- metric-only goals with no mechanism
- claims about behavior outside the mutable artifact boundary
- text that cannot be falsified by the benchmark

## Example Questions

Use questions like these when writing the file:

- What exact component are we trying to improve?
- Why do we think this component controls the metric meaningfully?
- What result would count as evidence for the claim?
- If the metric does not move, what should we conclude?

## Relationship To Other Contracts

`program.md` defines the project contract.

`hypothesis.md` defines the learning claim inside that contract.

`docs/ROUND_CONTRACT.md` defines how a round uses the hypothesis.

The three documents serve different purposes and should not be collapsed into one file.

## Enforcement

Serious projects in the project registry must include `hypothesis.md` as a setup artifact.

Bootstrap generation should create it automatically.

Future agents should treat a missing or stale hypothesis artifact as a project-discipline problem, not as a harmless omission.
