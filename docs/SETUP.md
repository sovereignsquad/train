# Setup

## Purpose

This document defines the current local setup path for contributors working on `{train}`.

It now includes the Reply-adapter policy learner lane, not just the earlier benchmark scaffolds.

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

## Current Reply Policy Loop Setup

To work on the `{reply}` / `{trinity}` / `{train}` loop locally, also prepare:

- `/Users/Shared/Projects/trinity`
- replayable `{trinity}` training bundles or exported traces

Expected local sequence:

1. bootstrap `{train}`
2. bootstrap `{trinity}`
3. generate or load Reply adapter training bundles
4. run learners and eval helpers

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

## Reply-Oriented Verification

Recommended checks for the current policy loop:

```bash
uv run pytest tests/test_trinity_training_bundle_loader.py
uv run pytest tests/test_trinity_tone_learner.py
uv run pytest tests/test_trinity_brevity_learner.py
uv run pytest tests/test_trinity_channel_formatting_learner.py
uv run pytest tests/test_trinity_policy_eval.py
```

Reply proof lane:

```bash
uv run python scripts/prove_reply_cycle.py
```

Provider connectivity:

```bash
uv run python scripts/check_providers.py
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
