# Self-Learning Fine-Tuning System

## Purpose

This document describes how `{train}` should use local fine-tuning components to build a stronger
offline self-learning loop over time.

The target outcome is not uncontrolled self-modification.

The target outcome is:

- better replay corpora every day
- better reviewed training signals every day
- better bounded adapters every day
- better governed local deployment every day

## Core Rule

The system must improve offline before it improves online.

That means:

- collect live traces outside the trainer
- convert traces into explicit datasets and review artifacts
- train offline
- evaluate offline
- package explicitly
- promote only after evidence is attached

Do not let local automation bypass those gates.

## Tool Roles

Each tool should have one job in the local AI system.

### `QLoRA`

Role:

- default training method

Use it for:

- low-cost supervised fine-tuning from accepted datasets
- later preference training when chosen/rejected pairs become stable enough

Why:

- lower memory requirements than full fine-tuning
- strong quality-to-cost ratio for local training
- best fit for the first bounded lane in `{train}`

### `mlx-lm`

Role:

- phase-one local training worker

Use it for:

- loading the base model
- applying `QLoRA`
- running the training job
- exporting adapter artifacts
- optionally exporting an Ollama-ready package later

Why:

- official Apple Silicon path
- explicit `LoRA` / `QLoRA` support through `mlx_lm.lora`
- local train, test, and generate workflow on Apple hardware

### `Ollama`

Role:

- local adapter serving and packaged inference target

Use it for:

- loading accepted adapters against a known base model
- running local inference after a training round is approved
- canarying accepted adapters in the local runtime

Do not use it as:

- the training framework

### `Unsloth`, `Axolotl`, and `LLaMA-Factory`

Role:

- not part of the active delivery plan

Reason:

- current delivery must stay Apple-Silicon-only
- `Unsloth` should not be treated as a primary path while its docs still frame Apple Silicon / MLX training support as in progress
- `Axolotl` and `LLaMA-Factory` are not the right fit for the first local Apple-Silicon lane

## `{train}` Component Roles

The existing repo already has most of the governance substrate.

### Dataset Registry

Existing role:

- store versioned datasets and saved slices

Use it to:

- register daily replay corpora
- pin the exact corpus version used for each training round
- keep supervised and preference-ready corpora separate

### Persistent Grader Suites

Existing role:

- hold reusable evaluation criteria

Use them to:

- evaluate every candidate adapter after training
- keep quality checks stable across days
- stop “better today” from meaning “different metric today”

### Hybrid Evaluators

Existing role:

- combine code, model-judge, and human-review inputs

Use them to:

- score adapters automatically
- attach model-judge evidence to training rounds
- keep a path for human overrides on important decisions

### Skeptical Review

Existing role:

- generate rejection-ready review artifacts

Use it to:

- prevent weak daily improvements from shipping
- record why a candidate should not be promoted
- surface dissent when one evaluator says “improved” and another says “regressed”

## Daily Learning Loop

The local system should run one bounded loop per day.

### Step 1: Collect Candidate Learning Material

Inputs:

- yesterday's `{trinity}` traces
- failed or low-scoring rows
- manual corrections
- accepted operator rewrites
- known regressions or dissent cases

Required output:

- one explicit raw replay slice candidate

Notes:

- this step is data collection, not training
- keep tenant and scope boundaries intact

### Step 2: Build Governed Training Corpora

Split the data into separate corpora:

- supervised corpus
- preference corpus
- holdout evaluation corpus
- hard-case regression corpus

Rules:

- do not train directly on the same rows used as the only acceptance evaluation
- keep one fixed holdout set for honest comparison
- preserve provenance for every row

This is where annotation discipline matters most.

“Self-learning” should mostly mean:

- good failure capture
- good row filtering
- good row labeling
- good holdout hygiene

not merely “run more fine-tunes”.

### Step 3: Create One Training Spec

Each daily run should create one explicit training spec artifact.

Minimum fields:

- round id
- dataset key and version
- optional slice key
- base model id
- training backend
- training method
- hyperparameters
- expected adapter family
- expected output path
- attached grader suite

Phase-one defaults:

- backend: `mlx-lm`
- method: `qlora`

### Step 4: Run Offline Training

Phase-one implementation:

- `{train}` launches one `mlx-lm` worker
- the worker resolves the registered dataset
- the worker runs one bounded `QLoRA` job
- the worker emits:
  - adapter artifact
  - training metadata
  - logs
  - base-model reference
  - template/tokenizer reference

This step must be reproducible from the training spec and dataset version.

### Step 5: Evaluate The Adapter

After training:

- run the attached grader suite
- compare against the incumbent adapter or incumbent prompt/policy artifact
- record disagreement rows
- generate skeptical review if the family is important enough or if the result is mixed

Promotion should require:

- explicit evaluation artifacts
- explicit pass/fail outcome
- explicit reviewer path for risky changes

### Step 6: Package For Local Runtime

If the adapter passes:

- package it for local use
- optionally create an Ollama model using the matching base model and adapter
- keep the packaging artifact separate from the training artifact

Important:

- the base model used by Ollama must match the base model used in training
- the same chat template and EOS handling must be preserved, or results can degrade

### Step 7: Controlled Adoption

Accepted adapters should first be:

- registered
- versioned
- linked to their evidence
- optionally canaried in a bounded local environment

Do not let the daily loop push directly into the live runtime with no review surface.

## What “Automatic” Should Mean

The correct automation shape is:

- schedule collection daily
- schedule corpus-building daily
- schedule one bounded training run daily if enough reviewed data exists
- schedule evaluation automatically after training
- require explicit promotion gates before wider adoption

The incorrect automation shape is:

- train on every new trace immediately
- replace the live runtime model automatically
- collapse dataset creation, training, evaluation, and promotion into one hidden job

## Phase Plan

### Phase 1

Build the narrow system that can already improve every day:

- daily replay-slice ingestion
- supervised corpus building
- one `mlx-lm` `QLoRA` worker
- one adapter artifact contract
- one grader-suite evaluation path
- one optional Ollama packaging step

This is enough to start real local teaching.

### Phase 2

After phase one is stable:

- add chosen/rejected preference corpora
- add `DPO` or `ORPO` training
- add better hard-negative mining
- add confidence and variance tracking
- keep the incumbent-versus-candidate comparison discipline unchanged

### Phase 3

Only after the above is solid:

- consider whether a second backend is needed at all
- consider larger models or more complex scheduling only if the Apple-Silicon path proves insufficient

## What Research Says To Do In Practice

### For `mlx-lm`

Use it in `{train}` as the worker that owns:

- model loading
- dataset formatting
- `QLoRA` setup
- training execution
- adapter export
- optional Ollama export

Local implementation implication:

- `{train}` should generate inputs for `mlx-lm`, not re-implement fine-tuning kernels itself

### For `Ollama`

Use it after training for:

- local model creation from base model plus adapter
- controlled inference and canary checks

Local implementation implication:

- `{train}` should create a deterministic `Modelfile` or call the local create API with explicit
  base model, adapter, template, and parameters

### For `Unsloth`, `Axolotl`, and `LLaMA-Factory`

Use them only as ecosystem references for now.

Local implementation implication:

- keep them out of the first automated learning path

## Recommended First Build Order

1. Implement the training spec contract.
2. Implement a supervised-corpus export path from the dataset registry.
3. Implement one `mlx-lm` `QLoRA` worker runner.
4. Implement adapter artifact persistence and metadata capture.
5. Implement grader-suite evaluation for trained adapters.
6. Implement optional Ollama packaging and local canary serving.
7. Add daily scheduling only after the above path is reproducible by hand.

## Sources

- [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314)
- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
- [MLX LM](https://github.com/ml-explore/mlx-lm)
- [MLX LM LoRA / QLoRA Guide](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md)
- [Unsloth Docs](https://unsloth.ai/docs)
- [Unsloth Installation](https://docs.unsloth.ai/get-started/install-and-update)
- [Ollama Modelfile Reference](https://docs.ollama.com/modelfile)
- [Ollama Create API](https://docs.ollama.com/api/create)
