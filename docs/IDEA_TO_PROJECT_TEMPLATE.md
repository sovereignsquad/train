# Idea To Project Template

## Purpose

This document explains how to turn a raw idea into a valid `{train}` project.

The goal is to make onboarding repeatable instead of bespoke.

## Use This Template When

- a new product or workflow needs bounded optimization
- a team wants to improve one component repeatedly under automatic evaluation
- the target may live inside another system such as `{trinity}`

## Required Translation

Every idea must be translated into five concrete choices:

1. optimization target
2. controlled mutable artifact
3. bounded run entrypoint
4. automatic score
5. keep-or-reject decision rule

If any of those remain vague, the idea is not ready to become a `{train}` project.

## Project Intake Checklist

Answer these questions explicitly:

1. What single component are we improving?
2. What one file or bounded file set is allowed to change?
3. What command runs one honest experiment?
4. What scalar metric decides success?
5. What setup and dependency files must remain protected?
6. What local artifacts or data are required?
7. What budget range keeps runs comparable?

## Mutable Artifact Rules

Choose the smallest artifact that can still produce meaningful improvement.

Prefer:

- one Python module
- one prompt or policy file
- one ranking or scoring file

Avoid:

- whole application folders
- mixed runtime and UI surfaces
- artifacts that imply many unrelated changes at once

## Run Entrypoint Rules

One project must map to one bounded command.

The run entrypoint must:

- accept a budget
- emit machine-readable JSON
- report one scalar metric
- fail closed on invalid output

## Metric Rules

The score must be:

- automatic
- scalar
- repeatable enough for ratchet decisions
- aligned with the mutable artifact

If the metric mainly measures another component, the project boundary is wrong.

## External Runtime Projects

Some `{train}` projects optimize components that live inside external runtime systems such as `{trinity}`.

For those projects:

- `{train}` owns the optimization contract
- the external runtime owns production execution
- the mutable artifact must still be copied or represented inside the project workspace explicitly
- the run entrypoint must evaluate the component without requiring the full production system to be rewritten into `{train}`

## Output

A project is ready only when it has:

- a project key
- a project folder
- a mutable artifact
- `program.md`
- `run_benchmark.py`
- setup artifacts
- dependency artifacts
- metric name and direction
- budget bounds

