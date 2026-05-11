# Hybrid Evaluators

## Purpose

This document defines the first bounded hybrid evaluator path in `{train}`.

Use it when one replayable review run needs to combine:

- code evaluators
- model-judge artifacts
- human-review artifacts

## Current Scope

The current lane supports:

- persistent evaluator definitions inside grader suites
- builtin code evaluator execution from comparison artifacts
- imported model-judge artifacts
- imported human-review artifacts
- disagreement reporting across evaluator types

It does not support:

- live model calls during review runs
- crowd workflow products
- hidden evaluator arbitration

## Evaluator Types

Current supported evaluator types are stored through the existing grader-suite interface:

- `code`
- `model`
- `human`

The current bounded posture is explicit:

- `code` evaluators execute inside `{train}`
- `model` evaluators are imported from explicit artifact files
- `human` evaluators are imported from explicit artifact files

## Imported Artifact Rule

Imported evaluator artifacts must remain auditable.

The current run request passes them by:

- `grader_key`
- absolute local artifact path

This keeps the hybrid run replayable without requiring live evaluator infrastructure.

## Current Reporting Shape

One hybrid run currently preserves:

- suite identity
- dataset identity
- proposal family
- proposal artifact version
- comparison artifact reference
- per-evaluator results
- disagreement rows when evaluator decisions diverge

## Current CLI Surface

- `python -m train_core.cli run-grader-suite`

Use `--evaluator-artifact-file grader_key=/absolute/path/to/artifact.json` to attach imported model
or human evaluator outputs.

## Current API Surface

- `POST /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/grader-suites/{suite_key}/versions/{suite_version}/runs`

## Design Rules

- preserve evaluator type differences instead of flattening them
- keep model and human artifacts auditable
- keep disagreement visible
- keep replay bounded to explicit local artifacts
- do not imply that one evaluator type is globally authoritative

## Related Documents

- `docs/PERSISTENT_GRADER_SUITES.md`
- `docs/TRINITY_SKEPTICAL_EVAL_REPORT_CONTRACT.md`
- `docs/COMPARISON_HARNESS.md`
- `docs/STATUS.md`
- `docs/HANDOVER.md`
