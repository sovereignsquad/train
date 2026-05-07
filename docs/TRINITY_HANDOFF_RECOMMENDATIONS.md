# {trinity} Handoff Recommendations

## Purpose

This document captures the recommended operating posture for the live `{trinity} -> {train} -> {trinity}` seam.

It is not the contract for the seam itself.

Use:

- `docs/TRINITY_TRAIN_HANDOFF_TEMPLATE.md` for the required handoff shape
- this document for the recommended adoption and safety posture

## Current Recommendation

`{trinity}` should use the `{train}` seam now, but only as a bounded proposal-and-review workflow.

It should not use it as silent autonomous self-modification.

## What Trinity Should Use First

Use the seam first for bounded Reply policy families:

- tone
- brevity
- channel formatting

These are good first candidates because:

- the mutable scope is narrow
- replay quality is understandable
- the policy effect is inspectable
- rollback is tractable

## What Trinity Should Not Use First

Do not start with:

- full reply generation
- retrieval policy with broad context effects
- multi-step orchestration
- send gating
- safety gates
- transport semantics

These are too broad or too risky for the current seam maturity.

## Acceptance Should Not Be The Default

The current seam can optionally accept immediately after proposal generation.

That is useful for:

- controlled tests
- fixture-driven local development
- explicit sandbox validation

That should not be the normal operating mode for serious runtime work.

Recommended default flow:

1. export bundles
2. call `{train}`
3. receive proposal artifact and eval report
4. replay in `{trinity}`
5. inspect scope and regression risk
6. accept explicitly

## Recommended Trinity Acceptance Gate

Before adopting a `{train}` proposal, `{trinity}` should require:

1. schema validation
2. scope validation
3. contract-version validation
4. replay against incumbent behavior
5. regression-threshold check
6. explicit rollback registration

If any of these are missing, acceptance is too weak.

## Holdout Recommendation

Do not accept on the same bundle corpus alone.

Use:

- proposal corpus
- small holdout corpus
- regression corpus when available

The seam becomes much more trustworthy when a proposal survives a second replay surface.

## Provenance Recommendation

Every accepted live cycle should preserve:

- accepted artifact version
- source `{train}` project key
- accepted `{train}` run id
- contract version
- scope kind
- scope value when present

Without this, later learning and rollback become blurry.

## Scope Recommendation

`{trinity}` should reject suspiciously broad proposals from narrow corpora.

Examples:

- one-company corpus attempting a channel-wide policy
- one-channel corpus attempting a global policy
- one niche thread family attempting a general runtime rule

The current company-aware scope work in `{train}` helps, but `{trinity}` should enforce the same caution on the runtime side.

## Runtime Ownership Recommendation

`{train}` should remain:

- proposal generator
- eval report generator
- bounded offline optimizer

`{trinity}` should remain:

- runtime owner
- precedence-rule owner
- accepted-artifact registry owner
- rollback owner
- production accountability layer

This split should not be blurred.

## Best Current Operating Mode

Recommended mode now:

- enabled for bounded policy proposal
- replay-gated
- explicit-accept by default
- rollback-ready
- provenance-heavy

Not recommended now:

- silent auto-accept in production
- broad multi-component learning
- whole-brain optimization claims

## Suggested Trinity Next Steps

The best next steps for `{trinity}` are:

1. strengthen the accepted-artifact registry
2. add a promotion review surface
3. require holdout replay before normal acceptance
4. harden scope rejection rules
5. preserve skeptical acceptance notes for future monitoring

## Decision Rule

If the question is "should `{trinity}` use this seam now?", the answer is:

- yes, for bounded policy proposal workflows
- no, for hidden autonomous runtime mutation
