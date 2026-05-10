# {trinity} Ranking-Learning Export Contract

## Purpose

This document defines the explicit `ranking-learning` export contract `{trinity}` must provide before
`{train}` can add the bounded ranking-policy learner tracked in issue `#30`.

It exists to keep one boundary hard:

- `{trinity}` owns live ranking behavior
- `{train}` consumes exported ranking snapshots offline

## Status

This is a contract-definition document, not a claim that the export already exists in `{trinity}`.

The contract is complete enough for:

- schema definition
- replay fixture generation
- benchmark design in `{train}`
- proposal and comparison planning

It is not an authorization for:

- direct reads from live runtime stores
- hidden runtime introspection from `{train}`
- silent promotion of accepted ranking proposals back into `{trinity}`

## Artifact Family

The artifact family name is:

- `ranking-learning`

The export package should describe one replayable ranking decision or one bounded ranking slice drawn
from a fixed corpus.

`{train}` should be able to run the same exported slice repeatedly and reach the same inputs for the
same ranking-policy candidate.

## Contract Version Rule

Every ranking-learning export must include:

- `contract_version`

The version should be namespaced under a Trinity ranking prefix, for example:

- `trinity.ranking.v1alpha1`

`{train}` should reject:

- missing contract versions
- unknown major versions
- mixed contract versions inside one declared replay corpus

## Export Unit

One ranking-learning record should represent one bounded ranking decision with enough context to replay
that decision offline.

The record must not require:

- live retrieval
- live memory lookup
- live product state access
- live operator UI state

## Required Fields

Each ranking-learning record must contain at least:

- `contract_version`
- `bundle_type`
- `component_key`
- `artifact_family`
- `runtime_artifact_version`
- `exported_at`
- `trace_ref`
- `cycle_id`
- `decision_id`
- `scope_kind`
- `scope_value` when scoped
- `input_context`
- `candidate_set`
- `selected_candidate_id`
- `selected_candidate_position`
- `selected_candidate_score`
- `feedback_disposition`
- `outcome_signal`

## Required Field Meaning

### Identity And Provenance

- `bundle_type`
  - must be `ranking-learning`
- `component_key`
  - identifies the runtime component being optimized, for example `reply_ranker`
- `artifact_family`
  - identifies the runtime artifact family, for example `ranking_policy`
- `runtime_artifact_version`
  - names the exact accepted `{trinity}` ranking artifact that produced the decision
- `exported_at`
  - export timestamp
- `trace_ref`
  - stable trace identifier for audit and replay provenance
- `cycle_id`
  - stable cycle identifier when one cycle includes multiple ranking decisions
- `decision_id`
  - stable identifier for the bounded ranking decision itself

### Scope

- `scope_kind`
  - expected values should stay explicit, for example `global`, `company`, or `channel`
- `scope_value`
  - required when the scope is not global

The export must not let a narrow corpus pretend to be broader than its actual scope.

### Input Context

`input_context` must contain the bounded inputs required to replay the ranking decision offline.

It should include at least:

- the operator or user request summary that triggered the ranking decision
- channel or surface metadata relevant to ranking
- any bounded context snapshot needed to score candidates
- the active policy provenance relevant to the decision

It must not include:

- opaque references that only `{trinity}` can dereference live
- direct handles to mutable runtime stores
- hidden dependencies on live retrieval side effects

### Candidate Set

`candidate_set` must contain the bounded alternatives that were available to the ranker at the moment of
decision.

Each candidate record should include at least:

- `candidate_id`
- `position`
- `content_ref` or bounded replay content
- `feature_summary`
- `score_breakdown`
- `is_selected`

`score_breakdown` should stay explicit enough that `{train}` can reason about why the incumbent ranker
preferred one candidate over another.

That does not require exposing every internal runtime detail, but it does require more than a single
opaque final score.

### Selected Outcome

The record must identify:

- `selected_candidate_id`
- `selected_candidate_position`
- `selected_candidate_score`

These should match one candidate inside `candidate_set`.

`{train}` should fail closed if the selected candidate cannot be matched deterministically.

### Feedback And Outcome

The export must include a bounded outcome signal for offline evaluation.

Required fields:

- `feedback_disposition`
- `outcome_signal`

`feedback_disposition` should classify the review outcome, for example:

- `CONFIRMED_GOOD`
- `CONFIRMED_BAD`
- `CORRECTED`
- `ABSTAIN`

`outcome_signal` should carry the replayable scalar or structured signal `{train}` will use to compare
ranking-policy candidates.

Examples:

- chosen candidate preserved by operator
- chosen candidate rewritten heavily
- chosen candidate displaced by another candidate
- ranking regret score derived from later operator preference

## Replayability Rules

The contract is valid only if the export is:

- deterministic from the same source decision
- replayable without live `{trinity}` access
- narrow enough to evaluate one ranking component honestly
- stable enough to support baseline/incumbent/candidate comparison

`{train}` should be able to build a fixed replay corpus from these exports and run:

1. incumbent ranking policy
2. candidate ranking policy
3. optional baseline policy

against the same decisions repeatedly.

## Rejection Rules

`{train}` should reject ranking-learning exports when:

- `bundle_type` is not `ranking-learning`
- `contract_version` is missing or incompatible
- required provenance fields are missing
- candidate identities are not stable
- selected candidate linkage is inconsistent
- outcome signals are missing or unreplayable
- scope metadata is missing or suspiciously broad for the corpus

## Example Shape

```json
{
  "contract_version": "trinity.ranking.v1alpha1",
  "bundle_type": "ranking-learning",
  "component_key": "reply_ranker",
  "artifact_family": "ranking_policy",
  "runtime_artifact_version": "reply_ranker.20260510.1",
  "exported_at": "2026-05-10T18:20:00Z",
  "trace_ref": "trace_123",
  "cycle_id": "cycle_456",
  "decision_id": "decision_789",
  "scope_kind": "channel",
  "scope_value": "email",
  "input_context": {
    "channel": "email",
    "thread_summary": "Operator asked for a concise customer reply",
    "policy_context": {
      "reply_policy_version": "reply_behavior_policy.tone.20260509"
    }
  },
  "candidate_set": [
    {
      "candidate_id": "cand_a",
      "position": 1,
      "feature_summary": {
        "length_bucket": "short"
      },
      "score_breakdown": {
        "ranking_score": 0.81
      },
      "is_selected": true
    },
    {
      "candidate_id": "cand_b",
      "position": 2,
      "feature_summary": {
        "length_bucket": "medium"
      },
      "score_breakdown": {
        "ranking_score": 0.74
      },
      "is_selected": false
    }
  ],
  "selected_candidate_id": "cand_a",
  "selected_candidate_position": 1,
  "selected_candidate_score": 0.81,
  "feedback_disposition": "CORRECTED",
  "outcome_signal": {
    "kind": "ranking_regret",
    "value": 0.42
  }
}
```

## What Remains Owned By {trinity}

Even with this export contract in place, `{trinity}` still owns:

- live candidate generation
- live ranking execution
- runtime precedence rules
- accepted ranking artifact registry
- runtime promotion and rollback

`{train}` remains:

- replay consumer
- proposal generator
- comparison/eval generator
- bounded offline optimizer

## Relationship To Issue #30

Issue `#30` becomes implementation-ready only after `{trinity}` exports an artifact family that matches
this contract closely enough for:

- fixture loading
- benchmark replay
- proposal generation
- comparison reporting

If the learner would still need to infer hidden runtime behavior, this contract is not yet satisfied.

## Related Documents

- `docs/TRINITY_LIVE_BRAIN_OPTIMIZATION_BOUNDARY.md`
- `docs/TRINITY_TRAIN_HANDOFF_TEMPLATE.md`
- `docs/TRINITY_FRONTIER_PROMOTION.md`
