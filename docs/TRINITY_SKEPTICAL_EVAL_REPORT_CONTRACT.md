# {train} Skeptical-Eval Report Contract

## Purpose

This document defines the explicit skeptical-eval report contract higher-risk proposal lanes must emit
before they should be treated as promotion-ready candidates for `{trinity}` review.

It exists to keep one boundary hard:

- `{train}` can propose and critique bounded artifact changes
- `{trinity}` still decides whether any proposal should be adopted into live runtime behavior

## Status

This is a contract-definition document, not a claim that every future learner family is already
implemented.

The contract is complete enough for:

- reusable skeptical review artifacts
- explicit rejection-ready evidence
- machine-readable minority views
- issue `#32` implementation planning

It is not an authorization for:

- automatic proposal promotion
- live runtime mutation
- replacing keep/reject discipline with generic commentary

## Artifact Family

The skeptical review artifact family name is:

- `skeptical-eval-report`

One skeptical-eval report should review one bounded proposal artifact or one bounded proposal family
comparison.

`{train}` should be able to regenerate the same skeptical-eval report inputs from the same replay
corpus, proposal artifact, and comparison outputs.

## Contract Version Rule

Every skeptical-eval report must include:

- `contract_version`

The version should be namespaced under a `{train}` skeptical-eval prefix, for example:

- `train.skeptical_eval.v1alpha1`

`{train}` should reject:

- missing contract versions
- unknown major versions
- mixed contract versions inside one declared skeptical review bundle

## Report Unit

One skeptical-eval report should represent one explicit review decision over one bounded proposal.

The report must not require:

- live `{trinity}` runtime reads
- hidden reviewer memory
- freeform chat context that exists only outside the repository
- product-side approval state

## Required Fields

Each skeptical-eval report must contain at least:

- `contract_version`
- `report_type`
- `component_key`
- `artifact_family`
- `proposal_artifact_version`
- `proposal_ref`
- `comparison_ref`
- `review_scope_kind`
- `review_scope_value` when scoped
- `generated_at`
- `review_outcome`
- `promotion_readiness`
- `primary_decision_summary`
- `rejection_evidence`
- `minority_report`
- `confidence_summary`
- `next_disproof_tests`

## Required Field Meaning

### Identity And Provenance

- `report_type`
  - must be `skeptical-eval-report`
- `component_key`
  - identifies the bounded component under review, for example `reply_ranker` or
    `memory_retriever`
- `artifact_family`
  - identifies the proposal family under review, for example `ranking_policy`,
    `retrieval_selection_policy`, or `prepared_draft_refresh_policy`
- `proposal_artifact_version`
  - names the exact candidate artifact version being reviewed
- `proposal_ref`
  - stable reference to the proposal artifact or proposal package
- `comparison_ref`
  - stable reference to the baseline/incumbent/candidate comparison output that informed the review
- `generated_at`
  - report generation timestamp

The skeptical-eval report must point to explicit proposal and comparison artifacts rather than
re-explaining the entire experiment inline.

### Scope

- `review_scope_kind`
  - expected values should stay explicit, for example `global`, `company`, or `channel`
- `review_scope_value`
  - required when the scope is not global

The review scope must not claim broader confidence than the replay corpus actually supports.

### Review Outcome

`review_outcome` must state the primary disposition from a skeptical reviewer perspective.

Expected values should stay explicit, for example:

- `ADVANCE_WITH_CAUTION`
- `HOLD_FOR_MORE_EVIDENCE`
- `REJECT_FOR_NOW`
- `ABSTAIN`

`promotion_readiness` must separately classify whether the proposal is ready for human adoption
review.

Expected values should stay explicit, for example:

- `PROMOTION_READY`
- `NOT_PROMOTION_READY`

This split matters because a report may acknowledge a promising direction while still refusing to
recommend promotion.

### Primary Decision Summary

`primary_decision_summary` must capture:

- the strongest plain-language assessment of the proposal
- why the proposal should advance, hold, or stop
- what comparison evidence mattered most

It should stay brief enough to read quickly, but specific enough that downstream reviewers do not
need to infer the decision from scattered notes.

### Rejection Evidence

`rejection_evidence` must be a machine-readable list, even when the final outcome is not full
rejection.

Each rejection evidence record should include at least:

- `reason_code`
- `severity`
- `evidence_summary`
- `supporting_signal`
- `blocking`

Expected `reason_code` examples:

- `OVERFIT_RISK`
- `WEAK_GENERALIZATION`
- `INSUFFICIENT_CORPUS`
- `UNCLEAR_CAUSALITY`
- `RUNTIME_BOUNDARY_RISK`
- `POLICY_REGRESSION`

Expected `severity` examples:

- `LOW`
- `MEDIUM`
- `HIGH`

At least one rejection evidence record is required when:

- `review_outcome` is `HOLD_FOR_MORE_EVIDENCE`
- `review_outcome` is `REJECT_FOR_NOW`
- `promotion_readiness` is `NOT_PROMOTION_READY`

### Minority Report

`minority_report` must preserve the strongest skeptical interpretation instead of collapsing all
dissent into a single confidence score.

The minority report must contain at least:

- `skeptical_summary`
- `hidden_confounds`
- `overfitting_risks`
- `weak_assumptions`
- `disconfirming_signals`

This field may be concise, but it must stay explicit whenever the proposal could be over-read.

### Confidence Summary

`confidence_summary` must explain why the review confidence is strong or weak.

It should include at least:

- corpus sufficiency assessment
- reproducibility assessment
- signal clarity assessment

Expected values may be short labels plus notes, but the report must make weak confidence visible.

### Next Disproof Tests

`next_disproof_tests` must list the concrete tests that would most effectively disprove optimistic
interpretations.

Each record should include at least:

- `test_name`
- `purpose`
- `expected_failure_signal`

This is required because skeptical review should end with a falsification path, not just cautionary
phrasing.

## Relationship To Comparison Outputs

The skeptical-eval report does not replace the comparison harness.

It sits on top of the comparison output and answers a different question:

- comparison asks whether the candidate appears better
- skeptical-eval asks whether that apparent improvement is trustworthy enough to advance

Every skeptical-eval report should point to one explicit comparison artifact rather than embedding a
second independent scoring system.

## Replayability Rules

The contract is valid only if the report is:

- tied to explicit bounded inputs
- reproducible from the same proposal and comparison artifacts
- narrow enough to review one bounded proposal honestly
- stable enough to preserve dissent across handoff and later audit

`{train}` should be able to regenerate skeptical review inputs without reopening live runtime state or
reconstructing missing chat context.

## Rejection Rules

`{train}` should reject skeptical-eval reports when:

- `report_type` is not `skeptical-eval-report`
- `contract_version` is missing or incompatible
- proposal provenance is missing
- comparison provenance is missing
- promotion readiness is omitted
- rejection evidence is empty when the report is not promotion-ready
- minority-report content is omitted for a higher-risk proposal lane
- next disproof tests are missing

## Example Shape

```json
{
  "contract_version": "train.skeptical_eval.v1alpha1",
  "report_type": "skeptical-eval-report",
  "component_key": "memory_retriever",
  "artifact_family": "retrieval_selection_policy",
  "proposal_artifact_version": "retrieval_selection_policy.candidate.20260510.1",
  "proposal_ref": "artifacts/proposals/retrieval_selection_policy.candidate.20260510.1.json",
  "comparison_ref": "artifacts/comparisons/retrieval_selection_policy.20260510.comparison.json",
  "review_scope_kind": "company",
  "review_scope_value": "acme",
  "generated_at": "2026-05-10T19:10:00Z",
  "review_outcome": "HOLD_FOR_MORE_EVIDENCE",
  "promotion_readiness": "NOT_PROMOTION_READY",
  "primary_decision_summary": "Candidate improved headline retrieval score, but the corpus is too narrow to trust cross-thread generalization.",
  "rejection_evidence": [
    {
      "reason_code": "WEAK_GENERALIZATION",
      "severity": "HIGH",
      "evidence_summary": "Improvement is concentrated in one customer thread cluster.",
      "supporting_signal": "gain disappears on holdout slice",
      "blocking": true
    }
  ],
  "minority_report": {
    "skeptical_summary": "The apparent gain may be a corpus-local shortcut rather than a better selector.",
    "hidden_confounds": [
      "holdout slice shares operator style with the training slice"
    ],
    "overfitting_risks": [
      "candidate appears tuned to one document source mix"
    ],
    "weak_assumptions": [
      "selected-document count is being treated as a proxy for relevance quality"
    ],
    "disconfirming_signals": [
      "candidate underperforms incumbent on manually corrected retrieval traces"
    ]
  },
  "confidence_summary": {
    "corpus_sufficiency": "weak",
    "reproducibility": "medium",
    "signal_clarity": "weak"
  },
  "next_disproof_tests": [
    {
      "test_name": "cross-company holdout replay",
      "purpose": "check whether the gain survives outside the current company slice",
      "expected_failure_signal": "candidate loses its advantage on unseen support histories"
    }
  ]
}
```

## Ownership Split

This report contract preserves the boundary:

- `{train}` may generate skeptical review artifacts for bounded offline proposals
- `{trinity}` remains responsible for adoption decisions, runtime rollout, and live monitoring

The skeptical-eval report informs promotion review.

It does not perform promotion.

## Relationship To Open Issues

This document closes the contract prerequisite in issue `#35`.

It exists so the broader skeptical-eval implementation lane in issue `#32` can build on an explicit
review artifact instead of inventing one ad hoc.

## Related Documents

- `docs/TRINITY_LIVE_BRAIN_OPTIMIZATION_BOUNDARY.md`
- `docs/TRINITY_TRAIN_HANDOFF_TEMPLATE.md`
- `docs/COMPARISON_HARNESS.md`
- `docs/ROUND_CONTRACT.md`
