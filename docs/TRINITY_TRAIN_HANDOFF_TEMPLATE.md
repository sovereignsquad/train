# {trinity} To {train} Handoff Template

## Purpose

This document defines the exact template for handing one `{trinity}` runtime component into `{train}` for bounded offline optimization.

Use it when a `{trinity}` behavior slice is ready to become a serious `{train}` project.

Do not use it for:

- live runtime execution
- whole-brain training
- product-side behavior in `{reply}`
- unbounded multi-component experiments

For the recommended operating posture after the seam exists, read:

- `docs/TRINITY_HANDOFF_RECOMMENDATIONS.md`

## Boundary Rule

The handoff is always:

1. `{trinity}` exports a bounded artifact or replay bundle
2. `{train}` evaluates and proposes improvements offline
3. `{trinity}` explicitly imports accepted improvements back into runtime-owned code or artifacts

`{train}` does not become part of the live drafting path.

## When A Trinity Component Is Ready

A `{trinity}` component is ready for `{train}` only when all of these are true:

1. the component can be named precisely
2. the mutable scope is bounded
3. the score path is automatic
4. the export is replayable
5. runtime ownership can remain inside `{trinity}`

If any of these are false, the component is not ready.

## Approved Component Shapes

Good first handoff candidates:

- ranking policy
- tone policy
- brevity policy
- channel-formatting policy
- retrieval weighting policy
- abstain/escalation policy

For the current contract definitions that gate richer Trinity handoffs, read:

- `docs/TRINITY_RANKING_LEARNING_EXPORT_CONTRACT.md`
- `docs/TRINITY_RETRIEVAL_SELECTION_EXPORT_CONTRACT.md`
- `docs/TRINITY_SKEPTICAL_EVAL_REPORT_CONTRACT.md`

Bad first handoff candidates:

- whole conversation runtime
- mixed UI and runtime behavior
- transport or send logic
- contact stitching
- cross-cutting orchestration with no single metric

## Trinity Export Package

`{trinity}` should export one bounded package per learning corpus or replay slice.

Minimum fields:

- `contract_version`
- `bundle_type`
- `component_key`
- `artifact_family`
- `runtime_artifact_version`
- `exported_at`
- `cycle_id`
- `thread_ref`
- `channel`
- `language`
- `selected_candidate_id`
- `selected_candidate_text`
- `final_text`
- `rewrite_severity`
- `feedback_disposition`

Recommended additional fields:

- `candidate_set`
- `candidate_scores`
- `trace_ref`
- `contact_scope_kind`
- `latency_ms`
- `operator_edits_summary`
- `notes`

## Export Rules

The export must be:

- deterministic from the same source cycle
- local-first
- versioned
- replayable without live product access
- narrow enough to evaluate one component honestly

The export must not:

- require direct database access from `{train}`
- leak product transport ownership
- mix unrelated runtime concerns into one bundle

## Train Project Files

Every serious Trinity-backed `{train}` project must contain:

- `program.md`
- `hypothesis.md`
- `prepare.py`
- `run_benchmark.py`
- one mutable artifact such as `train.py`
- one committed fixture or one local-only replay loader path

Example:

```text
projects/trinity_reply_ranker/
  program.md
  hypothesis.md
  prepare.py
  run_benchmark.py
  train.py
  eval_fixture.json
```

## Program Contract

`program.md` should state:

- what runtime component is being optimized
- what `{train}` owns
- what `{trinity}` still owns
- what file is mutable
- what score decides success

## Hypothesis Contract

`hypothesis.md` should state:

- component under optimization
- expected improvement
- why that improvement is expected
- metric expected to move
- what failure would mean

For Trinity-backed work, failure meaning should usually distinguish between:

- weak hypothesis
- bad export shape
- wrong project boundary
- runtime behavior that cannot be learned from this corpus alone

## Benchmark Entrypoint Contract

`run_benchmark.py` must:

- load one replay corpus or fixture set
- run the bounded artifact under a fixed budget
- emit machine-readable JSON
- report one scalar metric
- fail closed on malformed exports

The benchmark should compare:

- incumbent
- candidate
- baseline when relevant

For the standard comparison artifact shape, read:

- `docs/COMPARISON_HARNESS.md`

## Mutable Artifact Contract

The mutable artifact should be the smallest artifact that can express the learning claim.

Good examples:

- `train.py` with ranking weights
- `train.py` with tone preference synthesis logic
- `policy.md` with deterministic bounded formatting rules

Avoid:

- multiple unrelated files
- runtime-owned code copied wholesale from `{trinity}`
- artifacts whose score is mostly driven by another component

## Acceptance Gates Before Handoff

Before a Trinity component is accepted as a `{train}` project, confirm:

1. the bundle validates against a versioned contract
2. the benchmark replays locally without product access
3. the mutable artifact is bounded
4. the metric aligns with the component
5. the project has `program.md` and `hypothesis.md`

## Promotion Package Back To Trinity

An accepted `{train}` result should return:

- `component_key`
- `accepted_project_key`
- `accepted_run_id`
- `accepted_metric`
- `accepted_artifact_version`
- `proposal_artifact_path`
- `contract_version`
- `promotion_notes`

Optional:

- `minority_report_ref`
- `comparison_report_ref`
- `holdout_warnings`

## Promotion Rules

Promotion back into `{trinity}` must remain explicit.

Required sequence:

1. validate the accepted proposal artifact
2. map it into runtime-owned representation
3. run `{trinity}` tests and replay gates
4. register the new accepted runtime artifact version
5. keep one-step rollback available

`{train}` may propose.
`{trinity}` must decide runtime adoption.

## Example Handoff: Reply Ranker

Handoff:

- `{trinity}` exports ranked candidate traces plus selected outcomes
- `{train}` replays ranking alignment offline
- `{train}` proposes improved ranking logic
- `{trinity}` imports the accepted ranking policy back into runtime-owned code

Not included:

- send behavior
- UI behavior
- transport semantics
- live message retrieval

The concrete ranking-learning export shape for this family should follow:

- `docs/TRINITY_RANKING_LEARNING_EXPORT_CONTRACT.md`

## Example Handoff: Tone Policy

Handoff:

- `{trinity}` exports selected candidate text, final sent text, rewrite severity, language, and channel
- `{train}` learns bounded tone preference proposals
- `{trinity}` imports accepted tone policy artifacts into runtime policy resolution

Not included:

- product approval logic
- operator identity stitching
- whole reply generation stack

## Decision Rule

When deciding whether something belongs in this handoff:

- if it is live runtime behavior, keep it in `{trinity}`
- if it is product behavior, keep it in `{reply}`
- if it is a bounded offline improvement of a replayable Trinity component, move it into `{train}`

## Minimum Checklist

Before opening a new Trinity-backed `{train}` issue, confirm:

- component is named
- export exists
- contract version exists
- project boundary is narrow
- metric is automatic
- `program.md` exists
- `hypothesis.md` exists
- promotion path back into `{trinity}` is explicit
