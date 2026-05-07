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

## Verified Working

Verified locally in the current implementation lane:

- `uv run pytest`
- `uv run ruff check .`
- targeted Reply-adapter learner tests
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

## Immediate Next Steps

1. keep the new Trinity-callable proposal seam stable and explicit
2. expand invariant coverage around the optimizer core
3. keep proposal artifacts explicit and versioned
4. avoid turning `{train}` into a second runtime
5. avoid drifting into a generic prompt framework as the seam expands

## Resume Point

If resuming work, read:

1. [README.md](/Users/Shared/Projects/train/README.md)
2. [docs/STATUS.md](/Users/Shared/Projects/train/docs/STATUS.md)
3. [docs/HANDOVER.md](/Users/Shared/Projects/train/docs/HANDOVER.md)
4. [docs/SETUP.md](/Users/Shared/Projects/train/docs/SETUP.md)
