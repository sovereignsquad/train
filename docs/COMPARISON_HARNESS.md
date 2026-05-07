# Comparison Harness

## Purpose

This document defines the standard comparison harness for serious `{train}` work.

Use it when a project needs fixed baseline-versus-candidate-versus-incumbent evidence under the same corpus and the same evaluation path.

## Why This Exists

`{train}` already had:

- bounded runs
- automatic scores
- ratchet keep/reject behavior

What it lacked was a standard comparison artifact that made evidence reusable and hard to fake.

The comparison harness fixes that by requiring:

- fixed inputs
- fixed budget
- fixed evaluation path
- direct deltas
- one stable report shape

## Standard Shape

Every serious comparison should produce:

1. one metric name
2. one metric direction
3. one sample count
4. one row for each evaluated subject
5. direct deltas from baseline to candidate and incumbent to candidate when possible
6. one human-readable comparison table

## Standard Rows

Preferred row labels:

- `baseline`
- `incumbent`
- `candidate`

Each row should include:

- label
- artifact key
- version
- score when available
- status
- notes

If a row cannot be scored honestly, keep it in the report with:

- `status = metadata_only`

Do not invent scores for unavailable artifacts.

## Delta Rules

The comparison harness should compute direct deltas when both scores exist.

Preferred delta pairs:

- `candidate - baseline`
- `candidate - incumbent`

For maximize metrics:

- positive delta means improvement

For minimize metrics:

- negative delta means improvement

## Fixed Comparison Rules

The harness is only trustworthy when:

- inputs are the same
- evaluation path is the same
- execution budget is the same
- compared artifacts target the same bounded component

If any of those differ, the comparison is not valid.

## Current Reply-Policy Use

The first real harness use in this repo is the `{trinity}` Reply policy seam.

Current support:

- candidate proposal scoring on fixed training bundles
- optional baseline policy artifact scoring on the same bundle corpus
- optional incumbent policy artifact scoring on the same bundle corpus
- metadata-only incumbent row when the incumbent artifact content is not available
- machine-readable comparison report
- direct markdown comparison table

Current CLI/API surfaces:

- `python -m train_core.cli propose-reply-policy`
- `POST /v1/trinity/reply/policies/propose`

Optional inputs:

- `baseline_policy_file`
- `incumbent_policy_file`
- `comparison_output_path`

## Honesty Rule

Do not pretend a comparison is stronger than it is.

Examples:

- if the incumbent artifact content is unavailable, record it as metadata only
- if a baseline is omitted, do not fabricate one
- if the score is heuristic, say so in notes and project docs

The harness exists to improve rigor, not to generate cleaner-looking fiction.

## Reuse Rule

Future projects should reuse the same report shape even if their metric logic differs.

That means the harness should remain:

- component-agnostic
- machine-readable
- stable enough for round reports and minority reports later

## Relationship To Other Docs

- `docs/ROUND_CONTRACT.md` defines when comparison is required
- `docs/HYPOTHESIS_CONTRACT.md` defines what the comparison is supposed to test
- `docs/TRINITY_TRAIN_HANDOFF_TEMPLATE.md` defines how `{trinity}` components enter `{train}`

## Minimum Checklist

Before trusting a comparison report, confirm:

- the compared artifacts are bounded to the same component
- the sample corpus is fixed
- the metric direction is explicit
- the report includes direct deltas
- unavailable rows are marked honestly
