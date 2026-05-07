# Handover

## Purpose

This is the current resume document for `{train}`.

## Current Handover

### What Changed Last

Last meaningful tranche:

- `{train}` became the bounded offline consumer of `{trinity}` Reply adapter training bundles
- `{train}` now exposes a first-class proposal surface that `{trinity}` can call by API or CLI

Implemented or now present in the active working tree:

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

### What Was Verified

Verified:

- `uv run pytest`
- `uv run ruff check .`

### What Needs To Happen Next

1. decide whether `{train}` should own supervised API startup helpers or remain API-server passive
2. expand invariant coverage next
3. keep the Reply-adapter policy lane reproducible and bounded
4. avoid direct runtime mutation paths
5. do not let ecosystem inspiration turn `{train}` into a prompt framework

### Watch Carefully

- do not let `{train}` absorb live runtime behavior from `{trinity}`
- do not let proposal artifacts become implicit side effects
- keep policy provenance explicit and single-source
- keep replay corpora stable enough to support incumbent-vs-candidate evaluation
- do not regress company scope back to channel-only inference, or the Trinity isolation work will be undermined
- borrow eval rigor and optimization framing, but resist prompt-framework drift
