# {train}

`{train}` is the offline bounded optimizer for systems such as `{trinity}`.

It is not the product shell and it is not the live runtime.

Current split:

- `{reply}` is the product
- `{trinity}` is the live drafting runtime
- `{train}` improves bounded policy slices from exported traces and bundles

## Current Role In The Reply Policy Loop

`{train}` currently exists to consume replayable `{trinity}` artifacts and emit explicit proposals, not hidden runtime mutations.

Current Reply-adapter policy work in this repo covers:

- Trinity training-bundle ingestion
- tone policy proposal generation
- brevity policy proposal generation
- channel-formatting policy proposal generation
- incumbent-vs-candidate policy eval reporting
- API and CLI proposal surfaces for Trinity to request bounded Reply behavior policy proposals

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

## Current Reply-Oriented Capabilities

Delivered or in active working tree:

- `TrinityTrainingBundleRecord` ingestion schemas
- trace and training-bundle loaders
- bounded tone learner
- bounded brevity learner
- bounded channel-formatting learner
- reply policy eval report builder

These all operate on explicit Reply-adapter bundle inputs and explicit proposal outputs.

Current adapter posture:

- `{trinity}` is now adapter-aware at the runtime and CLI layer
- `{train}` currently consumes only Reply adapter artifacts
- broad multi-adapter training support is not implemented yet

## Setup And Run Surfaces

API:

```bash
uv run uvicorn train_api.main:app --reload
```

Reply policy proposal CLI:

```bash
uv run python -m train_core.cli propose-reply-policy \
  --learner-kind tone \
  --bundle-file /absolute/path/to/bundle.json \
  --proposal-output-path /absolute/path/to/proposal.json \
  --eval-output-path /absolute/path/to/eval_report.json
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

`{train}` may not:

- change live runtime behavior directly
- own send semantics
- bypass explicit artifact promotion and replay gates

## Docs To Read First

- [docs/STATUS.md](/Users/Shared/Projects/train/docs/STATUS.md)
- [docs/HANDOVER.md](/Users/Shared/Projects/train/docs/HANDOVER.md)
- [docs/SETUP.md](/Users/Shared/Projects/train/docs/SETUP.md)
- [docs/HYPOTHESIS_CONTRACT.md](/Users/Shared/Projects/train/docs/HYPOTHESIS_CONTRACT.md)
- [docs/POLICY_LOOP_REPO_BREAKDOWN.md](/Users/Shared/Projects/train/docs/POLICY_LOOP_REPO_BREAKDOWN.md)

## License

This project is licensed under `Apache-2.0`.
