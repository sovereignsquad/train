# Offline Training Contracts

## Purpose

This document defines the first contract layer for `{train}`'s offline fine-tuning lane.

It does not define the worker implementation.
It defines the artifacts the worker must consume and emit.

## Active Delivery Constraint

The active delivery plan is Apple-Silicon-only.

That means:

- the first local backend target is `mlx-lm`
- the contract should remain backend-aware but not depend on `Unsloth`, `Axolotl`, or `LLaMA-Factory`
- `Ollama` remains a serving target after training, not the training backend

## Training Spec

The training spec is the explicit input contract for one bounded offline training run.

Current persisted fields:

- `key`
- `version`
- `name`
- `description`
- `dataset_key`
- `dataset_version`
- optional `dataset_slice_key`
- optional `dataset_slice_version`
- `grader_suite_key`
- `grader_suite_version`
- `base_model_ref`
- `base_model_source_kind`
- `template_ref`
- optional `tokenizer_ref`
- `training_backend`
- `training_stage`
- `training_method`
- `expected_adapter_family`
- `output_dir`
- `hyperparameters`
- `provenance`

Current validation rules:

- dataset version must exist
- dataset slice must exist if specified
- grader suite must exist on the same dataset version
- `output_dir` must be absolute
- local-path `base_model_ref` values must resolve inside `TRAIN_MODELS_ROOT`
- current allowed backends:
  - `mlx-lm`
  - `external`
- current allowed base model source kinds:
  - `huggingface`
  - `ollama`
  - `local-path`
- current allowed training stages:
  - `sft`
  - `dpo`
  - `orpo`
  - `kto`
- current allowed training methods:
  - `qlora`
  - `lora`
  - `full-finetune`
- `mlx-lm` training specs may use `huggingface` or `local-path` base model refs, but not `ollama`

## Adapter Artifact

The adapter artifact is the explicit output contract for one trained adapter package.

Current persisted fields:

- `key`
- `version`
- `training_spec_key`
- `training_spec_version`
- `name`
- `description`
- inherited dataset and grader-suite provenance from the training spec
- inherited base model, template, tokenizer, backend, stage, and method from the training spec
- `adapter_family`
- `adapter_format`
- `artifact_path`
- optional `checkpoint_path`
- optional `training_log_path`
- optional `packaging_metadata_path`
- `provenance`

Current validation rules:

- referenced training spec must exist
- `artifact_path` must be absolute
- optional paths must be absolute when present
- current allowed adapter formats:
  - `safetensors`
  - `gguf`
  - `ollama`

## API Surface

Current routes:

- `GET /v1/training-specs`
- `POST /v1/training-specs`
- `GET /v1/training-specs/{spec_key}/versions/{spec_version}`
- `DELETE /v1/training-specs/{spec_key}/versions/{spec_version}`
- `GET /v1/training-specs/{spec_key}/versions/{spec_version}/readiness`
- `GET /v1/adapter-artifacts`
- `POST /v1/adapter-artifacts`
- `GET /v1/adapter-artifacts/{artifact_key}/versions/{artifact_version}`
- `DELETE /v1/adapter-artifacts/{artifact_key}/versions/{artifact_version}`
- `POST /v1/adapter-artifacts/{artifact_key}/versions/{artifact_version}/ollama-package`
- `GET /v1/doctor`
- `POST /v1/training-specs/{spec_key}/versions/{spec_version}/self-learning-cycle`

## CLI Surface

Current CLI commands:

- `python -m train_core.cli run-training-spec`
- `python -m train_core.cli check-training-readiness`
- `python -m train_core.cli package-adapter-artifact-for-ollama`
- `python -m train_core.cli run-daily-self-learning-cycle`

Current proof and smoke scripts:

- `python scripts/check_operator_clients.py`
- `python scripts/prove_trinity_train_handoff.py`
- `python scripts/check_packaged_release_contract.py`

Current behavioral rules:

- `doctor --workflow training` treats offline training readiness as required, not advisory
- `check-training-readiness` resolves local-path model refs through `TRAIN_MODELS_ROOT`
- `package-adapter-artifact-for-ollama` only packages persisted adapter artifacts with `safetensors`
- `run-daily-self-learning-cycle` keeps evaluation explicit by requiring a comparison report before promotion or packaging can be considered ready

## Boundary Rules

These contracts are governance artifacts, not runtime artifacts.

They may:

- point at governed datasets
- declare a bounded local training run
- capture trained adapter provenance

They may not:

- change live runtime behavior directly
- imply promotion into `{trinity}`
- bypass evaluation, skeptical review, or packaging discipline

## Why This Layer Exists First

Without these contracts:

- a training worker would hide assumptions in scripts
- adapters would be hard to replay or evaluate honestly
- later scheduling would automate undocumented behavior

This layer remains the governance substrate for the current `mlx-lm` worker and any later evaluation, packaging, or promotion flow built on top of it.
