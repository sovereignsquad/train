# Trinity Live Brain Optimization Boundary

## Purpose

This document defines the implementable `{train}` role once `{trinity}` grows into a full live-brain runtime with memory, retrieval, and prepared drafts.

It exists to prevent a category error:

`{train}` improves the live brain.
`{train}` does not become the live brain.

## Non-Negotiable Boundary

`{train}` remains the bounded offline optimizer.

It may:

- consume exported `{trinity}` traces and bundles
- evaluate candidate policies against bounded corpora
- generate explicit proposal artifacts
- compare baseline, incumbent, and candidate behavior

It may not:

- own live memory stores
- answer runtime retrieval queries
- hold canonical operator/contact/thread state
- generate live prepared drafts for `{reply}`
- mutate `{trinity}` runtime state directly

## What Changes When `{trinity}` Becomes A Live Brain

The optimizer surface becomes richer, but the boundary does not move.

As `{trinity}` adds:

- contact memory
- self profile memory
- thread summaries
- prepared draft cache
- retrieval policies

`{train}` may only consume exported bounded views of those behaviors for offline analysis.

Examples of valid future optimizer artifacts:

- ranking-weight policy
- retrieval-selection policy
- summary-regeneration policy thresholds
- contact-memory salience policy
- prepared-draft refresh threshold policy

Examples of invalid ownership drift:

- live vector database ownership
- live document chunk retrieval
- live contact fact storage
- product-side send execution policy

## Required Artifact Families

The existing Reply policy bundle families remain valid:

- `tone-learning`
- `brevity-learning`
- `channel-formatting-learning`

Future bounded artifact families should be added only when `{trinity}` exports them explicitly:

- `ranking-learning`
- `retrieval-selection-learning`
- `summary-refresh-learning`
- `prepared-draft-refresh-learning`

Each artifact family must stay:

- explicit
- versioned
- replayable
- narrow enough to review and reject

For the first explicit ranking-family contract definition, read:

- `docs/TRINITY_RANKING_LEARNING_EXPORT_CONTRACT.md`

For the first explicit retrieval-family contract definition, read:

- `docs/TRINITY_RETRIEVAL_SELECTION_EXPORT_CONTRACT.md`

## Required Export Shape From `{trinity}`

For `{train}` to improve richer runtime behavior safely, `{trinity}` must export:

- thread context metadata
- retrieval context summary
- selected memory facts
- prepared draft metadata
- operator edit distance and final outcome
- active artifact provenance

That export must still avoid handing `{train}` live mutable state.

`{train}` should ingest snapshots of runtime behavior, not mount or read runtime stores directly.

## Optimizer Architecture Role

Within `{train}`, the richer live-brain future maps to these layers:

- `adapter.provider.*`
  - provider inventory and model access where needed for offline evaluation
- `adapter.agent.*`
  - autonomous optimization agents for benchmark or proposal generation workflows
- `engine.*`
  - artifact loading, replay, comparison, scoring, proposal generation
- `ops.*`
  - run lifecycle, recovery, persistence, API surfaces

For the live-brain program, the relevant addition is in `engine.*`, not in runtime ownership.

## Comparison To Current Implementation

Already implemented:

- training-bundle ingestion
- bounded Reply policy learners
- bounded Spot review-policy learner
- evaluation reports
- comparison harness
- proposal API and CLI surfaces
- provider and agent registries

Not yet implemented, and not currently required:

- learners for runtime ranking policies
- learners for retrieval-selection policies
- learners for prepared-draft refresh policies
- richer minority-report and skeptical-eval lanes for brain-oriented proposals

## Comparison To Open GitHub Issues

Checked against the public GitHub issue list on May 10, 2026.

Already aligned:

- issue `#1` provider-neutral autonomous optimization platform remains the umbrella
- issue `#28` minority-report support becomes more important once proposals affect richer runtime behavior
- issue `#30` tracks the future ranking-policy learner lane
- issue `#31` tracks the future retrieval-selection learner lane
- issue `#32` tracks the broader skeptical-eval lane
- issue `#33` tracks the ranking-learning export contract prerequisite
- issue `#34` tracks the retrieval-selection export contract prerequisite
- issue `#35` tracks the skeptical-eval report contract prerequisite

## Current Board Read

The learner issues already exist, but they should not be treated as immediately implementable.

Current actionable unblockers:

1. define the ranking-learning export contract in issue `#33`
2. define the retrieval-selection export contract in issue `#34`
3. define the skeptical-eval report contract in issue `#35`

The broader learner lanes in `#30`-`#32` still depend on explicit `{trinity}` exports and review seams.

## Delivery Order

1. keep current Reply policy learners stable
2. define and preserve explicit export contracts before learner implementation begins
3. add one learner at a time with explicit replay and comparison reports
4. preserve review and promotion discipline in `{trinity}`

## Acceptance Criteria

This optimizer boundary remains healthy only if:

1. `{train}` can improve richer runtime policies without reading live runtime stores
2. every new learner consumes an explicit exported artifact family
3. accepted proposals still require `{trinity}` review and promotion
4. `{train}` never becomes the live memory or retrieval authority
