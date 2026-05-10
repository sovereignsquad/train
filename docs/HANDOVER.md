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
- Spot review-policy proposal service from bundle files
- `/v1/trinity/spot/policies/propose` endpoint
- `python -m train_core.cli propose-spot-review-policy` CLI surface

### What Was Verified

Verified:

- `uv run pytest`
- `uv run ruff check .`

### What Needs To Happen Next

1. decide whether `{train}` should own supervised API startup helpers or remain API-server passive
2. define the ranking-learning export contract tracked in GitHub issue `#33` before attempting learner work from `#30`
3. define the retrieval-selection export contract tracked in GitHub issue `#34` before attempting learner work from `#31`
4. define the skeptical-eval report contract tracked in GitHub issue `#35` before treating the broader `#32` lane as immediate implementation work
5. keep the Reply-adapter policy lane reproducible and bounded
6. avoid direct runtime mutation paths
7. do not let ecosystem inspiration turn `{train}` into a prompt framework
8. keep the Spot lane bounded to review-policy until Trinity has company-scoped Spot adoption and broader Spot artifact contracts

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
