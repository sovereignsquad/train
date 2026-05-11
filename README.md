# {train}

`{train}` is the offline bounded optimizer for systems such as `{trinity}`.

It is not the product shell and it is not the live runtime.

Current split:

- `{reply}` is the product
- `{trinity}` is the live drafting runtime
- `{train}` improves bounded policy slices from exported traces and bundles

## Current Policy Proposal Role

`{train}` currently exists to consume replayable `{trinity}` artifacts and emit explicit proposals, not hidden runtime mutations.

Current bounded proposal work in this repo covers:

- eval dataset registry with versioned corpora and saved slices
- persistent grader suites attached to datasets and proposal families
- Trinity training-bundle ingestion
- tone policy proposal generation
- brevity policy proposal generation
- channel-formatting policy proposal generation
- Spot review-policy proposal generation
- incumbent-vs-candidate policy eval reporting
- skeptical-eval report generation for higher-risk proposal review
- API and CLI proposal surfaces for Trinity to request bounded Reply and Spot policy proposals

## Current Dependency Surface

Base requirements:

- Python `>=3.12`
- `uv`

Project metadata:

- [pyproject.toml](/Users/Shared/Projects/train/pyproject.toml)

Runtime dependencies:

- `alembic>=1.16.0`
- `fastapi>=0.116.0`
- `pydantic-settings>=2.11.0`
- `sqlalchemy>=2.0.40`
- `uvicorn>=0.35.0`

Dev dependencies:

- `pytest>=8.4.0`
- `ruff>=0.12.0`

Optional toolchain:

- `Node.js` and `npm` for `apps/web`
- Swift / Xcode for `apps/macos`

## Local Setup

Bootstrap:

```bash
cd /Users/Shared/Projects/train
uv sync --extra dev
```

Validation:

```bash
uv run ruff check .
uv run pytest
```

## Current Bounded Capabilities

Delivered or in active working tree:

- eval dataset registry and saved slice model
- persistent grader-suite registry and rerun layer
- `TrinityTrainingBundleRecord` ingestion schemas
- `TrinitySpotTrainingBundleRecord` ingestion schemas
- trace and training-bundle loaders
- bounded tone learner
- bounded brevity learner
- bounded channel-formatting learner
- bounded Spot review-policy learner
- reply and Spot policy eval report builders
- skeptical-eval report builder for proposal review artifacts

These all operate on explicit exported bundle inputs and explicit proposal outputs.

Current adapter posture:

- `{trinity}` is now adapter-aware at the runtime and CLI layer
- `{train}` currently consumes Reply adapter artifacts plus the first bounded Spot review-policy artifact family
- broad multi-adapter training support beyond Reply and the first Spot slice is not implemented yet

## Setup And Run Surfaces

API:

```bash
uv run uvicorn train_api.main:app --reload
```

Eval dataset registry API:

- `GET /v1/eval-datasets`
- `POST /v1/eval-datasets`
- `GET /v1/eval-datasets/{dataset_key}/versions/{dataset_version}`
- `POST /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/slices`
- `POST /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/grader-suites`

Reply policy proposal CLI:

```bash
uv run python -m train_core.cli propose-reply-policy \
  --learner-kind tone \
  --bundle-file /absolute/path/to/bundle.json \
  --proposal-output-path /absolute/path/to/proposal.json \
  --eval-output-path /absolute/path/to/eval_report.json
```

Spot review-policy proposal CLI:

```bash
uv run python -m train_core.cli propose-spot-review-policy \
  --learner-kind review-policy \
  --bundle-file /absolute/path/to/spot_bundle.json \
  --proposal-output-path /absolute/path/to/spot_proposal.json \
  --eval-output-path /absolute/path/to/spot_eval_report.json
```

Reply policy proposal from a registered dataset:

```bash
uv run python -m train_core.cli propose-reply-policy \
  --learner-kind tone \
  --eval-dataset-key reply_tone_corpus \
  --eval-dataset-version 2026-05-11.1
```

Persistent grader-suite rerun CLI:

```bash
uv run python -m train_core.cli run-grader-suite \
  --dataset-key reply_tone_corpus \
  --dataset-version 2026-05-11.1 \
  --suite-key core_review \
  --suite-version 2026-05-11.1 \
  --proposal-family reply_behavior_policy \
  --proposal-artifact-version reply_behavior_policy.tone.candidate.v2 \
  --comparison-report-file /absolute/path/to/comparison_report.json
```

Skeptical-eval review CLI:

```bash
uv run python -m train_core.cli build-skeptical-eval-report \
  --component-key memory_retriever \
  --artifact-family retrieval_selection_policy \
  --proposal-artifact-version retrieval_selection_policy.candidate.v1 \
  --proposal-ref /absolute/path/to/proposal.json \
  --comparison-report-file /absolute/path/to/comparison_report.json \
  --review-scope-kind company \
  --review-scope-value company-1
```

Provider checks:

```bash
uv run python scripts/check_providers.py
```

Reply proof / benchmark lane:

```bash
uv run python scripts/prove_reply_cycle.py
```

## Product Boundary Rule

`{train}` may:

- consume exported `{trinity}` bundles
- generate proposal artifacts
- generate eval reports
- generate skeptical review artifacts

`{train}` may not:

- change live runtime behavior directly
- own send semantics
- bypass explicit artifact promotion and replay gates

## Docs To Read First

- [docs/STATUS.md](/Users/Shared/Projects/train/docs/STATUS.md)
- [docs/HANDOVER.md](/Users/Shared/Projects/train/docs/HANDOVER.md)
- [docs/SETUP.md](/Users/Shared/Projects/train/docs/SETUP.md)
- [docs/EVAL_DATASET_REGISTRY.md](/Users/Shared/Projects/train/docs/EVAL_DATASET_REGISTRY.md)
- [docs/PERSISTENT_GRADER_SUITES.md](/Users/Shared/Projects/train/docs/PERSISTENT_GRADER_SUITES.md)
- [docs/CODING_STANDARDS.md](/Users/Shared/Projects/train/docs/CODING_STANDARDS.md)
- [docs/HYPOTHESIS_CONTRACT.md](/Users/Shared/Projects/train/docs/HYPOTHESIS_CONTRACT.md)
- [docs/POLICY_LOOP_REPO_BREAKDOWN.md](/Users/Shared/Projects/train/docs/POLICY_LOOP_REPO_BREAKDOWN.md)

## License

This project is licensed under `Apache-2.0`.
