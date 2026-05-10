# {trinity} Retrieval-Selection Export Contract

## Purpose

This document defines the explicit `retrieval-selection-learning` export contract `{trinity}` must
provide before `{train}` can add the bounded retrieval-selection learner tracked in issue `#31`.

It exists to keep one boundary hard:

- `{trinity}` owns live retrieval behavior and memory access
- `{train}` consumes exported retrieval-selection snapshots offline

## Status

This is a contract-definition document, not a claim that the export already exists in `{trinity}`.

The contract is complete enough for:

- schema definition
- replay fixture generation
- benchmark design in `{train}`
- proposal and comparison planning

It is not an authorization for:

- direct reads from live vector stores or memory stores
- hidden runtime introspection from `{train}`
- silent promotion of accepted retrieval proposals back into `{trinity}`

## Artifact Family

The artifact family name is:

- `retrieval-selection-learning`

The export package should describe one replayable retrieval-selection decision or one bounded retrieval
slice drawn from a fixed corpus.

`{train}` should be able to run the same exported slice repeatedly and reach the same retrieval inputs
for the same retrieval-selection policy candidate.

## Contract Version Rule

Every retrieval-selection-learning export must include:

- `contract_version`

The version should be namespaced under a Trinity retrieval prefix, for example:

- `trinity.retrieval.v1alpha1`

`{train}` should reject:

- missing contract versions
- unknown major versions
- mixed contract versions inside one declared replay corpus

## Export Unit

One retrieval-selection-learning record should represent one bounded retrieval decision with enough
context to replay that decision offline.

The record must not require:

- live vector search
- live memory lookup
- live product state access
- live operator UI state

## Required Fields

Each retrieval-selection-learning record must contain at least:

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
- `query_context`
- `candidate_documents`
- `selected_document_ids`
- `selection_summary`
- `feedback_disposition`
- `outcome_signal`

## Required Field Meaning

### Identity And Provenance

- `bundle_type`
  - must be `retrieval-selection-learning`
- `component_key`
  - identifies the runtime component being optimized, for example `memory_retriever`
- `artifact_family`
  - identifies the runtime artifact family, for example `retrieval_selection_policy`
- `runtime_artifact_version`
  - names the exact accepted `{trinity}` retrieval artifact that produced the decision
- `exported_at`
  - export timestamp
- `trace_ref`
  - stable trace identifier for audit and replay provenance
- `cycle_id`
  - stable cycle identifier when one cycle includes multiple retrieval decisions
- `decision_id`
  - stable identifier for the bounded retrieval decision itself

### Scope

- `scope_kind`
  - expected values should stay explicit, for example `global`, `company`, or `channel`
- `scope_value`
  - required when the scope is not global

The export must not let a narrow corpus pretend to be broader than its actual scope.

### Query Context

`query_context` must contain the bounded inputs required to replay the retrieval decision offline.

It should include at least:

- the user or operator request summary that triggered retrieval
- bounded thread or task context relevant to retrieval
- channel or surface metadata relevant to selection
- active policy provenance relevant to the decision

It must not include:

- opaque handles that only `{trinity}` can dereference live
- direct references to mutable runtime stores
- hidden dependencies on live retrieval side effects

### Candidate Documents

`candidate_documents` must contain the bounded retrieval alternatives that were available to the selector
at the moment of decision.

Each candidate record should include at least:

- `document_id`
- `rank_position`
- `document_summary`
- `source_kind`
- `selection_features`
- `score_breakdown`
- `is_selected`

`selection_features` and `score_breakdown` should stay explicit enough that `{train}` can reason about
why the incumbent retrieval selector preferred some candidates over others.

That does not require exposing every internal runtime detail, but it does require more than an opaque
selected set.

### Selected Outcome

The record must identify:

- `selected_document_ids`
- `selection_summary`

`selected_document_ids` should match one or more candidates inside `candidate_documents`.

`selection_summary` should state the bounded retrieval result in a replayable way, for example:

- number of retrieved documents
- top-k behavior
- whether a key supporting fact was included

`{train}` should fail closed if selected document IDs cannot be matched deterministically.

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
retrieval-selection policy candidates.

Examples:

- retrieved set supported the final answer
- retrieved set omitted a key fact later added by the operator
- retrieved set included low-value or distracting documents
- retrieval regret score derived from later operator preference or downstream correction

## Replayability Rules

The contract is valid only if the export is:

- deterministic from the same source decision
- replayable without live `{trinity}` access
- narrow enough to evaluate one retrieval component honestly
- stable enough to support baseline/incumbent/candidate comparison

`{train}` should be able to build a fixed replay corpus from these exports and run:

1. incumbent retrieval-selection policy
2. candidate retrieval-selection policy
3. optional baseline policy

against the same retrieval decisions repeatedly.

## Rejection Rules

`{train}` should reject retrieval-selection-learning exports when:

- `bundle_type` is not `retrieval-selection-learning`
- `contract_version` is missing or incompatible
- required provenance fields are missing
- document identities are not stable
- selected document linkage is inconsistent
- outcome signals are missing or unreplayable
- scope metadata is missing or suspiciously broad for the corpus

## Example Shape

```json
{
  "contract_version": "trinity.retrieval.v1alpha1",
  "bundle_type": "retrieval-selection-learning",
  "component_key": "memory_retriever",
  "artifact_family": "retrieval_selection_policy",
  "runtime_artifact_version": "memory_retriever.20260510.1",
  "exported_at": "2026-05-10T18:40:00Z",
  "trace_ref": "trace_456",
  "cycle_id": "cycle_789",
  "decision_id": "decision_012",
  "scope_kind": "company",
  "scope_value": "acme",
  "query_context": {
    "channel": "email",
    "request_summary": "Find prior pricing commitments for this customer",
    "policy_context": {
      "retrieval_policy_version": "retrieval_selection_policy.20260509"
    }
  },
  "candidate_documents": [
    {
      "document_id": "doc_1",
      "rank_position": 1,
      "document_summary": "Prior renewal discount note",
      "source_kind": "crm_note",
      "selection_features": {
        "matched_customer": true
      },
      "score_breakdown": {
        "retrieval_score": 0.92
      },
      "is_selected": true
    },
    {
      "document_id": "doc_2",
      "rank_position": 2,
      "document_summary": "General pricing FAQ",
      "source_kind": "knowledge_base",
      "selection_features": {
        "matched_customer": false
      },
      "score_breakdown": {
        "retrieval_score": 0.64
      },
      "is_selected": false
    }
  ],
  "selected_document_ids": ["doc_1"],
  "selection_summary": {
    "selected_count": 1,
    "top_k": 1
  },
  "feedback_disposition": "CONFIRMED_GOOD",
  "outcome_signal": {
    "kind": "retrieval_regret",
    "value": 0.08
  }
}
```

## What Remains Owned By {trinity}

Even with this export contract in place, `{trinity}` still owns:

- live vector search
- live memory access
- live retrieval execution
- runtime precedence rules
- accepted retrieval artifact registry
- runtime promotion and rollback

`{train}` remains:

- replay consumer
- proposal generator
- comparison/eval generator
- bounded offline optimizer

## Relationship To Issue #31

Issue `#31` becomes implementation-ready only after `{trinity}` exports an artifact family that matches
this contract closely enough for:

- fixture loading
- benchmark replay
- proposal generation
- comparison reporting

If the learner would still need to infer hidden runtime behavior or live retrieval state, this
contract is not yet satisfied.

## Related Documents

- `docs/TRINITY_LIVE_BRAIN_OPTIMIZATION_BOUNDARY.md`
- `docs/TRINITY_TRAIN_HANDOFF_TEMPLATE.md`
- `docs/TRINITY_HANDOFF_RECOMMENDATIONS.md`
