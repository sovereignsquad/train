# Setup

## Purpose

This document defines the current local setup path for contributors working on `{train}`.

It now includes the bounded Reply and Spot policy learner lanes plus the skeptical-eval review lane,
not just the earlier benchmark scaffolds.

## Required Base Tools

- `git`
- `Python 3.12+`
- `uv`
- `Node.js` and `npm` if you need `apps/web`
- `Swift 6+` and Xcode Command Line Tools if you need `apps/macos`
- optional: `vibe` via `uv tool install mistral-vibe`

## Python Environment

Bootstrap:

```bash
cd /Users/Shared/Projects/train
uv sync --extra dev
```

Core validation:

```bash
uv run ruff check .
uv run pytest
```

## Current Policy Loop Setup

To work on the current `{trinity}` / `{train}` policy loops locally, also prepare:

- `/Users/Shared/Projects/trinity`
- replayable `{trinity}` training bundles or exported traces

Expected local sequence:

1. bootstrap `{train}`
2. bootstrap `{trinity}`
3. generate or load Reply or Spot training bundles
4. run learners, comparison helpers, and skeptical review helpers

## API And UI

API:

```bash
uv run uvicorn train_api.main:app --reload
```

Web UI:

```bash
cd apps/web
npm install
TRAIN_API_URL=http://127.0.0.1:8000 npm run dev
```

Native shell:

```bash
cd apps/macos
swift build -c release
bash Scripts/build-bundle.sh
open dist/train.app
```

If the native shell cannot resolve `uv` from its launch environment:

```bash
export TRAIN_UV_EXECUTABLE="$(command -v uv)"
```

## Bounded Policy Verification

Recommended checks for the current policy loop:

```bash
uv run pytest tests/test_trinity_training_bundle_loader.py
uv run pytest tests/test_trinity_tone_learner.py
uv run pytest tests/test_trinity_brevity_learner.py
uv run pytest tests/test_trinity_channel_formatting_learner.py
uv run pytest tests/test_trinity_policy_eval.py
uv run pytest tests/test_trinity_spot_training_bundle_loader.py
uv run pytest tests/test_trinity_spot_policy_service.py
uv run pytest tests/test_trinity_skeptical_eval.py
```

Reply proof lane:

```bash
uv run python scripts/prove_reply_cycle.py
```

Provider connectivity:

```bash
uv run python scripts/check_providers.py
```

Spot proposal lane:

```bash
uv run python -m train_core.cli propose-spot-review-policy \
  --learner-kind review-policy \
  --bundle-file /absolute/path/to/spot_bundle.json
```

Skeptical review lane:

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

## Environment Rules

- never commit secrets
- keep local overrides in `.env`
- document expected variables in [docs/ENVIRONMENT.md](/Users/Shared/Projects/train/docs/ENVIRONMENT.md)
- keep runtime and state paths out of the repo working tree unless intentionally repo-local

## Non-Goals

This setup should not require:

- direct live runtime mutation of `{trinity}`
- hosted deployment
- a packaged desktop release flow
- broad cloud dependencies beyond the declared local dev surface
