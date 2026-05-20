# Model Storage Audit

## Purpose

This document records the current model and AI asset storage posture for `{train}` and defines a
practical centralization plan around:

- `/Users/Shared/Models`

It is an audit and implementation plan, not an implementation claim.

## Audit Summary

`{train}` does not currently have one central model root.

Today the system splits model-related concerns across three different patterns:

1. hosted provider access by API
2. local provider access through `Ollama`
3. offline fine-tuning metadata and artifacts stored as absolute filesystem paths

That means `/Users/Shared/Models` already exists as a machine-level model vault, but `{train}` does
not yet treat it as a first-class source of truth.

## Current Storage Surfaces

### 1. Hosted provider models

Hosted provider use is configuration-only today.

Current implementation:

- `core/train_core/providers.py` defines the `mistral-api` adapter
- `core/train_core/config.py` stores `MISTRAL_API_KEY` and `MISTRAL_API_BASE_URL`

Current behavior:

- model inventory is read from `GET /v1/models` on the provider
- no hosted model weights are stored in the repo
- no local cache location is owned by `{train}`

### 2. Local provider models through Ollama

Local provider use is also indirect today.

Current implementation:

- `core/train_core/providers.py` defines the `ollama` adapter
- the adapter reads model names from `OLLAMA_BASE_URL + /api/tags`

Current behavior:

- `{train}` knows model names exposed by the running `Ollama` daemon
- `{train}` does not manage where `Ollama` stores those models on disk
- `{train}` does not import from `/Users/Shared/Models` into `Ollama`

### 3. Offline fine-tuning base models

The first offline training lane stores references, not a governed local model registry.

Current implementation:

- `core/train_core/fine_tuning.py`
- `core/train_core/mlx_lm_worker.py`
- `core/train_core/schemas.py`
- `core/train_core/models.py`

Current behavior:

- each training spec stores `base_model_ref`, `template_ref`, and optional `tokenizer_ref`
- those fields are free-form strings
- the `mlx-lm` worker passes `base_model_ref` directly to `mlx_lm.lora --model`
- no validation requires the base model to live under `/Users/Shared/Models`
- no shared path-resolution layer exists

### 4. Training outputs and adapter artifacts

Training outputs are stored as absolute paths chosen per training spec.

Current behavior:

- each training spec stores an absolute `output_dir`
- the worker writes outputs under:
  - `<output_dir>/<spec_key>/<spec_version>/<adapter_key>/<adapter_version>/`
- adapter artifacts store absolute `artifact_path`
- logs and metadata also store absolute paths

This is explicit and replayable, but not centralized by default.

### 5. Eval and grader artifacts

Eval dataset items and imported evaluator artifacts are also path-based.

Current behavior:

- dataset item paths must be absolute
- grader artifact inputs are read from absolute paths
- there is no shared asset-root convention for model-judge artifacts

## Existing Machine-Level Vault

`/Users/Shared/Models` already exists and is populated.

Observed categories include:

- `/Users/Shared/Models/llms/chat`
- `/Users/Shared/Models/llms/encoders`
- `/Users/Shared/Models/loras`
- `/Users/Shared/Models/adapters`
- `/Users/Shared/Models/checkpoints`
- `/Users/Shared/Models/vae`
- `/Users/Shared/Models/controlnet`
- `/Users/Shared/Models/processors`
- `/Users/Shared/Models/.cache/huggingface`

Observed LLM-relevant assets include:

- `gemma-4-e2b-it-gguf-4bit`
- `gemma-3-270m-it-mlx-8bit`
- `granite-4.0-h-350m-4bit`
- `qwen2.5-0.5b-instruct-4bit`
- `all-MiniLM-L6-v2`
- `multilingual-e5-small`
- `bert-base-uncased`

Important boundary:

- most of the vault is broader than `{train}`
- the vault includes image, diffusion, restoration, and segmentation assets that `{train}` does not
  currently use
- `{train}` should centralize around the vault without pretending all vault assets are train-owned

## Main Gaps

The current gaps are:

1. no `TRAIN_MODELS_ROOT` setting exists
2. no model path resolver exists in platform code
3. no registry exists for approved local base models
4. no distinction exists between model refs that are:
   - hosted identifiers
   - `Ollama` names
   - local absolute paths
   - local paths relative to a governed root
5. no packaging path exists from `{train}` adapter outputs into central local serving targets
6. the operator UI can show provider-reported models, but not centrally governed filesystem models

## Recommended Centralization Shape

### Decision

Use `/Users/Shared/Models` as the machine-level SSOT root for local AI assets, while keeping:

- hosted provider models external
- provider adapters separate from filesystem storage
- explicit artifact paths and promotion gates intact

### Root Contract

Add one explicit platform setting:

- `TRAIN_MODELS_ROOT=/Users/Shared/Models`

Then treat the following as governed subtrees for `{train}`:

- `llms/chat/`
- `llms/encoders/`
- `adapters/`
- `loras/`
- `.cache/huggingface/`

Optional later subtrees for packaging or output:

- `train/adapter-artifacts/`
- `train/ollama/`
- `train/manifests/`

This keeps the shared vault intact while giving `{train}` its own bounded areas.

## Proposed Path Rules

### Base model references

Support two explicit kinds only:

1. external model refs
   - example: `mlx-community/Llama-3.2-3B-Instruct-4bit`
2. local model refs under `TRAIN_MODELS_ROOT`
   - example: `llms/chat/gemma-3-270m-it-mlx-8bit`

Do not keep using ambiguous free-form strings forever.

Recommended stored fields:

- `base_model_ref`
- `base_model_source_kind`

Allowed values for `base_model_source_kind`:

- `huggingface`
- `ollama`
- `local-path`

For `local-path`, store the path relative to `TRAIN_MODELS_ROOT`, not a hard-coded absolute path.

### Tokenizers and templates

Apply the same rule to:

- `template_ref`
- `tokenizer_ref`

If local, store them relative to `TRAIN_MODELS_ROOT`.

### Training outputs

Move toward a default output root under the same vault:

- `/Users/Shared/Models/train/adapter-artifacts`

That gives one central place for:

- generated adapters
- training logs
- packaging metadata
- reproducible artifacts for later serving or evaluation

### Hugging Face cache

If the local toolchain depends on Hugging Face downloads, point cache directories into the shared
vault instead of per-user hidden directories.

Recommended machine-level cache root:

- `/Users/Shared/Models/.cache/huggingface`

`{train}` should document and prefer that path when local downloads are required.

## Phased Plan

### Phase 1. Define the contract

Add documentation and settings support for:

- `TRAIN_MODELS_ROOT`
- central local model-root semantics
- relative-path rules for local model references

Acceptance checks:

- env var is documented in `docs/ENVIRONMENT.md`
- config exposes the setting
- docs explain which subtrees are train-relevant

### Phase 2. Add a model resolver layer

Add one narrow reusable platform module such as:

- `engine.model_registry` or `engine.model_resolution`

Responsibilities:

- resolve local relative refs against `TRAIN_MODELS_ROOT`
- preserve hosted refs as hosted refs
- validate that local refs stay inside the governed root
- classify refs by source kind

Acceptance checks:

- local refs resolve deterministically
- path traversal outside the root fails closed
- worker code stops handling raw refs directly

### Phase 3. Tighten training-spec contracts

Extend the training-spec schema so base-model inputs are explicit.

Recommended additions:

- `base_model_source_kind`
- optional `base_model_resolved_path` at execution time only

Validation goals:

- local-path refs must resolve inside `TRAIN_MODELS_ROOT`
- `mlx-lm` local runs can use either a remote repo id or a validated local path

Acceptance checks:

- training-spec validation catches invalid local refs
- worker metadata records the fully resolved execution path

### Phase 4. Centralize adapter outputs

Adopt one default output root:

- `/Users/Shared/Models/train/adapter-artifacts`

Keep per-spec subdirectories under that root.

Acceptance checks:

- training specs can omit ad hoc output roots in the common case
- adapter artifact paths become predictable and searchable

### Phase 5. Add inventory and operator visibility

Expose central local model inventory through API and native operator UI.

Suggested API surface:

- `GET /v1/models/local`
- `GET /v1/models/local/chat`
- `GET /v1/models/local/encoders`

Suggested payload:

- relative ref
- absolute resolved path
- family
- format
- size if cheaply available
- last modified time

Acceptance checks:

- operator can see what local models are actually available
- training-spec creation can choose from governed local models

### Phase 6. Add packaging bridges

After adapter training is stable, add explicit packaging flows from:

- `{train}` adapter artifacts

to:

- central `Ollama` import assets
- optional future local serving manifests

Do not make packaging implicit.

Acceptance checks:

- one explicit packaging command exists
- packaging metadata is stored beside the produced artifact

## What Not To Do

Do not:

- move provider adapter logic into filesystem scanning code
- make `/Users/Shared/Models` a hard-coded path with no env override
- force all current vault categories into `{train}` ownership
- hide model downloads in random home-directory caches once the root contract exists
- let training outputs scatter across arbitrary temp locations by default

## Recommended Next Implementation Issue

The next bounded issue should be:

- add `TRAIN_MODELS_ROOT` plus a local model-resolution layer for training specs and adapter artifacts

That is the smallest correct step because it:

- preserves provider boundaries
- keeps the implementation local-first
- creates one reusable path contract before UI or packaging work expands

## Current Bottom Line

Today `{train}` stores model-related information in configuration, SQLite metadata, and arbitrary
absolute filesystem paths, but it does not centrally own local model storage.

The right path is not to force all model behavior into one adapter.
The right path is to make `/Users/Shared/Models` the governed local asset root and then layer:

1. config
2. path resolution
3. training-spec validation
4. centralized outputs
5. inventory and packaging

on top of that root.
