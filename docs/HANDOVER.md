# Handover

## Purpose

This is the current resume document for `{train}`.

## Current Handover

### What Changed Last

Last meaningful tranche:

- repo now contains an explicit optimizer-boundary document for the future `{reply}` live-brain system
- `{train}` became the bounded offline consumer of `{trinity}` Reply adapter training bundles
- `{train}` now exposes a first-class proposal surface that `{trinity}` can call by API or CLI
- `{train}` now also consumes bounded Spot training bundles for the first review-policy slice and can emit proposal/eval/comparison artifacts by API or CLI for Trinity adoption
- Spot review-policy proposals now carry explicit scope, so one-company corpora emit company-scoped artifacts that Trinity can adopt without cross-tenant leakage
- open-source docs and comment guidance were tightened so README, setup, boundary docs, coding standards, and handover/status files describe the same bounded Reply-plus-Spot reality
- the ranking-learning export contract required before future Trinity ranking-policy learner work is now defined explicitly in-repo
- the retrieval-selection export contract required before future Trinity retrieval learner work is now defined explicitly in-repo
- the skeptical-eval report contract required before broader brain-adjacent review work is now defined explicitly in-repo
- the first bounded skeptical-eval implementation lane now exists in code, API, CLI, and tests for higher-risk proposal review
- the first bounded eval dataset registry now exists in code, API, dataset/slice persistence, and tests so proposal lanes can reuse corpora instead of raw file lists

Implemented or now present in the active working tree:

- `docs/TRINITY_LIVE_BRAIN_OPTIMIZATION_BOUNDARY.md`
- Trinity training-bundle ingestion schemas
- trace and bundle loader helpers
- bounded tone learner
- bounded brevity learner
- bounded channel-formatting learner
- reply policy eval report builder
- reply policy proposal service from bundle files
- `/v1/trinity/reply/policies/propose` endpoint
- `python -m train_core.cli propose-reply-policy` CLI surface
- company-aware scope inference so one-company corpora do not collapse into channel-wide proposals
- first-class `hypothesis.md` contract plus project/bootstrap support
- standard comparison harness for baseline/incumbent/candidate policy reporting
- docs aligned around the `{reply}` / `{trinity}` / `{train}` operating split
- docs and inline comment standards now explicitly require public documentation to stay aligned with shipped behavior
- `docs/TRINITY_RANKING_LEARNING_EXPORT_CONTRACT.md`
- `docs/TRINITY_RETRIEVAL_SELECTION_EXPORT_CONTRACT.md`
- `docs/TRINITY_SKEPTICAL_EVAL_REPORT_CONTRACT.md`
- `docs/EVAL_DATASET_REGISTRY.md`
- eval dataset registry service and dataset-slice resolver
- `/v1/eval-datasets` dataset registry endpoints
- skeptical-eval report builder from comparison artifacts
- `/v1/trinity/reviews/skeptical-eval` endpoint
- `python -m train_core.cli build-skeptical-eval-report` CLI surface
- Spot review-policy proposal service from bundle files
- `/v1/trinity/spot/policies/propose` endpoint
- `python -m train_core.cli propose-spot-review-policy` CLI surface

### What Was Verified

Verified:

- `uv run pytest`
- `uv run ruff check .`
- targeted Spot and Reply proposal tests after the documentation consistency pass
- ranking-export contract documentation pass for issue `#33`
- retrieval-export contract documentation pass for issue `#34`
- skeptical-eval report contract documentation pass for issue `#35`
- targeted skeptical-eval implementation tests for issue `#32`
- targeted eval dataset registry implementation tests for issue `#36`

### What Needs To Happen Next

1. decide whether `{train}` should own supervised API startup helpers or remain API-server passive
2. build persistent grader suites in GitHub issue `#37` on top of the new dataset registry substrate
3. keep the Reply-adapter policy lane reproducible and bounded
4. avoid direct runtime mutation paths
5. do not let ecosystem inspiration turn `{train}` into a prompt framework
6. keep the Spot lane bounded to review-policy until Trinity has company-scoped Spot adoption and broader Spot artifact contracts
7. keep README, coding standards, setup, boundary docs, and handover/status docs in sync whenever bounded capability scope changes
8. do not start `#30` implementation until real `{trinity}` exports satisfy the ranking-learning contract document
9. do not start `#31` implementation until real `{trinity}` exports satisfy the retrieval-selection contract document

### Watch Carefully

- do not let `{train}` absorb live runtime behavior from `{trinity}`
- do not let proposal artifacts become implicit side effects
- keep policy provenance explicit and single-source
- keep replay corpora stable enough to support incumbent-vs-candidate evaluation
- do not regress company scope back to channel-only inference, or the Trinity isolation work will be undermined
- borrow eval rigor and optimization framing, but resist prompt-framework drift
- do not let future “brain” language blur the ownership line: `{train}` improves exported artifacts, `{trinity}` remains the live runtime
- do not overstate the current Spot support: `{train}` now has a first bounded Spot proposal/eval lane, not a broad Spot optimizer surface
- do not drop the new scope discipline: one-company Spot corpora must stay company-scoped unless Trinity’s adoption contract is intentionally widened later
- do not let public docs drift back to Reply-only wording while dataset-registry, Spot, and skeptical-review support are present in the shipped repo
