# Persistent Grader Suites

## Purpose

This document defines the first bounded persistent grader-suite layer in `{train}`.

Use it when evaluation criteria should persist across proposal variants instead of being recreated for
each run.

## Current Scope

The current grader-suite layer supports:

- versioned grader suites attached to one dataset version
- explicit attachment to one proposal family
- code-based grader definitions
- model-based grader references
- bounded reruns against new comparison artifacts

It does not support:

- live traffic grading
- remote grader marketplaces
- hidden grader mutation between runs

## Suite Identity

One suite is identified by:

- dataset `key`
- dataset `version`
- suite `key`
- suite `version`

The stable rendered suite reference is:

- `dataset_key@dataset_version:suite_key@suite_version`

## Current Grader Shape

Each grader stores:

- `grader_key`
- `grader_kind`
- `entrypoint_ref`
- `metric_name`
- optional `pass_threshold`
- optional `config`

Current allowed `grader_kind` values:

- `code`
- `model`

Current bounded execution posture:

- builtin `code` graders execute
- `model` graders are preserved as persistent references but are not executed yet

## Current Builtin Code Graders

The first bounded builtin grader entrypoints are:

- `builtin://candidate-vs-incumbent-delta`
- `builtin://candidate-vs-baseline-delta`
- `builtin://minimum-sample-count`

These operate on the existing comparison artifact, not on live runtime state.

## Rerun Contract

One suite rerun currently requires:

- dataset key and version
- suite key and version
- proposal family
- proposal artifact version
- comparison report file

The rerun output preserves:

- suite identity
- dataset identity
- proposal family
- proposal artifact version
- comparison artifact reference
- per-grader results

## Current API Surface

- `GET /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/grader-suites`
- `POST /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/grader-suites`
- `GET /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/grader-suites/{suite_key}/versions/{suite_version}`
- `DELETE /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/grader-suites/{suite_key}/versions/{suite_version}`
- `POST /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/grader-suites/{suite_key}/versions/{suite_version}/runs`

## Current CLI Surface

- `python -m train_core.cli run-grader-suite`

## Design Rules

- keep grader identity explicit and versioned
- keep dataset and proposal-family attachment visible
- keep execution bounded to explicit replay artifacts
- keep changed assumptions visible by versioning the suite
- do not let persistent graders imply automatic promotion authority

## Related Documents

- `docs/EVAL_DATASET_REGISTRY.md`
- `docs/COMPARISON_HARNESS.md`
- `docs/TRINITY_SKEPTICAL_EVAL_REPORT_CONTRACT.md`
- `docs/STATUS.md`
- `docs/HANDOVER.md`
