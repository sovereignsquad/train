# Status

## Purpose

This is the current status document for `{train}`.

## Current Phase

Phase:

- bounded optimizer role clarified
- Reply-adapter policy bundle consumer lane implemented
- tone, brevity, and channel-formatting proposal surfaces added
- incumbent-vs-candidate reply policy eval reporting added
- Trinity-callable Reply policy proposal API and CLI added
- first-class `hypothesis.md` contract added for serious `{train}` projects
- standard comparison harness added for the Trinity Reply policy seam

Primary active lane:

- keep the Reply-adapter optimization loop explicit and reproducible rather than broadening into hidden runtime mutation
- document and preserve the optimizer boundary as `{trinity}` grows toward a fuller live-brain runtime
- add bounded non-Reply artifact families only when `{trinity}` exports and promotion seams are explicit enough to keep adoption governed

## Current Reality

The repository currently has:

- Python platform scaffold
- FastAPI local API
- native macOS shell
- web operator UI
- project registry and run lifecycle
- provider registry and operator recovery
- reference benchmark projects
- `{trinity}` trace and training-bundle ingestion models
- bounded Reply-adapter tone learner
- bounded Reply-adapter brevity learner
- bounded Reply-adapter channel-formatting learner
- Reply-adapter policy eval report builder
- `/v1/trinity/reply/policies/propose` API endpoint
- `python -m train_core.cli propose-reply-policy` CLI entrypoint
- company-aware scope inference for Reply policy proposals
- fixed-shape baseline/incumbent/candidate comparison reporting for Reply policy proposals
- repo-resident optimizer-boundary spec for the live-brain direction in `docs/TRINITY_LIVE_BRAIN_OPTIMIZATION_BOUNDARY.md`
- repo-resident ranking-learning export contract spec for the future `{trinity}` ranking-family seam in `docs/TRINITY_RANKING_LEARNING_EXPORT_CONTRACT.md`
- first bounded Spot training-bundle consumer and review-policy learner/eval path
- `/v1/trinity/spot/policies/propose` API endpoint
- `python -m train_core.cli propose-spot-review-policy` CLI entrypoint
- Spot review-policy proposals now emit explicit scope, with one-company corpora producing company-scoped artifacts and multi-company corpora reserved for global artifacts

## Verified Working

Verified locally in the current implementation lane:

- `uv run pytest`
- `uv run ruff check .`
- targeted Reply-adapter learner tests
- targeted Spot review-policy tests
- Reply proof lane through `scripts/prove_reply_cycle.py`

## Current Gaps

Still intentionally not owned by `{train}`:

- live runtime behavior
- product transport semantics
- direct artifact promotion into `{trinity}`
- fully unattended API-server lifecycle ownership from `{trinity}`; the server still needs to be running when API transport is selected

Still open:

- broader comparison harnesses and invariants beyond the first Reply-adapter slice
- more explicit minority-report and skeptical-eval lanes
- longer unattended operator/runtime recovery exercises
- richer Trinity runtime artifact families have not been exported yet, so no ranking or retrieval learners should be added ahead of those contracts
- the ranking-learning export contract lane from GitHub issue `#33` is now defined in-repo; the next contract blocker is retrieval-selection in `#34`
- the skeptical-eval report contract should be pulled forward as explicit contract work via GitHub issue `#35` before the broader implementation lane in `#32`
- Spot proposal/eval support is still only the first review-policy slice; no broader Spot threshold/routing/prompt artifact families are implemented yet
- Spot scope support is still intentionally narrow: only `company` and `global` are supported for the first review-policy slice
- public docs must keep describing the current bounded Reply-plus-Spot state accurately; do not let README or contributor docs drift back to Reply-only wording

## Immediate Next Steps

1. keep the new Trinity-callable proposal seam stable and explicit
2. define the retrieval-selection export contract so issue `#31` becomes actually actionable
3. pull the skeptical-eval report shape forward as explicit contract work through issue `#35`, ahead of the broader implementation lane in `#32`
4. keep proposal artifacts explicit and versioned
5. avoid turning `{train}` into a second runtime
6. avoid drifting into a generic prompt framework as the seam expands
7. keep live-brain memory and prepared-draft ownership out of `{train}` even if future artifact families widen
8. keep the new Spot learner slice bounded; do not let it imply live Spot runtime mutation or workbook ownership

## Resume Point

If resuming work, read:

1. [README.md](/Users/Shared/Projects/train/README.md)
2. [docs/STATUS.md](/Users/Shared/Projects/train/docs/STATUS.md)
3. [docs/HANDOVER.md](/Users/Shared/Projects/train/docs/HANDOVER.md)
4. [docs/SETUP.md](/Users/Shared/Projects/train/docs/SETUP.md)
