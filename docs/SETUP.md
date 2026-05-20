# Setup

## Purpose

This document defines the current local setup path for contributors working on `{train}`.

It now includes the eval dataset registry, persistent grader suites, hybrid evaluator support, the
bounded Reply and Spot policy learner lanes, and the skeptical-eval review lane, not just the
earlier benchmark scaffolds.

## Required Base Tools

- `git`
- `Python 3.12+`
- `uv`
- `Node.js` and `npm` if you need `apps/web`
- `Swift 6+` and Xcode Command Line Tools if you need `apps/macos`
- optional: `vibe` via `uv tool install mistral-vibe`
- optional for the Apple-Silicon fine-tuning lane: `uv sync --extra dev --extra local-training`

## Python Environment

Bootstrap:

```bash
cd /Users/Shared/Projects/train
uv sync --extra dev
uv sync --extra dev --extra local-training
```

Optional shared local model root:

```bash
export TRAIN_MODELS_ROOT=/Users/Shared/Models
```

Use this when local training specs or future local model inventory should resolve against the
machine-level shared model vault instead of ad hoc per-user paths.

Use the `local-training` extra only on the Apple-Silicon machine that should execute the `mlx-lm`
lane. It is optional for general repo development.

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
4. optionally register reusable corpora and saved slices
5. run learners, comparison helpers, and skeptical review helpers

Current relation map and audit:

- see [docs/INTEGRATION_SURFACE.md](/Users/Shared/Projects/train/docs/INTEGRATION_SURFACE.md) for the current dependency/reference inventory and the latest local health-check results

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
uv run pytest tests/test_eval_datasets.py
uv run pytest tests/test_grader_suites.py
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

Dataset registry lane:

Use the local API to register one reusable corpus, then save durable slices under it.

See [docs/EVAL_DATASET_REGISTRY.md](/Users/Shared/Projects/train/docs/EVAL_DATASET_REGISTRY.md) for
the current dataset and slice shape.

Persistent grader-suite lane:

```bash
uv run python -m train_core.cli run-grader-suite \
  --dataset-key reply_tone_corpus \
  --dataset-version 2026-05-11.1 \
  --suite-key core_review \
  --suite-version 2026-05-11.1 \
  --proposal-family reply_behavior_policy \
  --proposal-artifact-version reply_behavior_policy.tone.candidate.v2 \
  --comparison-report-file /absolute/path/to/comparison_report.json \
  --evaluator-artifact-file model_judge=/absolute/path/to/model_judge.json \
  --evaluator-artifact-file human_review=/absolute/path/to/human_review.json
```

Apple-Silicon offline training lane:

```bash
uv run python -m train_core.cli run-training-spec \
  --spec-key reply_sft \
  --spec-version 2026-05-13.1 \
  --adapter-key reply_adapter_candidate \
  --adapter-version 2026-05-13.1 \
  --adapter-name "Reply Adapter Candidate" \
  --adapter-description "First mlx-lm QLoRA candidate"
```

Relation doctor and training-readiness lane:

```bash
uv run python -m train_core.cli doctor --workflow default --output-format summary
uv run python -m train_core.cli check-training-readiness \
  --spec-key reply_sft \
  --spec-version 2026-05-13.1
```

Local Ollama packaging lane:

```bash
uv run python -m train_core.cli package-adapter-artifact-for-ollama \
  --artifact-key reply_adapter_candidate \
  --artifact-version 2026-05-13.1 \
  --ollama-model-name train-reply-adapter:2026-05-13.1
```

Bounded daily self-learning lane:

```bash
uv run python -m train_core.cli run-daily-self-learning-cycle \
  --spec-key reply_sft \
  --spec-version 2026-05-13.1 \
  --adapter-key reply_adapter_candidate \
  --adapter-version 2026-05-13.1 \
  --adapter-name "Reply Adapter Candidate" \
  --adapter-description "Daily bounded training candidate" \
  --comparison-report-file /absolute/path/to/comparison_report.json
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

Operator-client contract smoke:

```bash
uv run python scripts/check_operator_clients.py
```

Cross-repo `{trinity}` handoff proof:

```bash
uv run python scripts/prove_trinity_train_handoff.py
```

Packaged release contract preflight:

```bash
uv run python scripts/check_packaged_release_contract.py
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
- a signed or notarized desktop release flow for local development
- broad cloud dependencies beyond the declared local dev surface
