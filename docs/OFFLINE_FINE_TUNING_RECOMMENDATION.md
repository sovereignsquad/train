# Offline Fine-Tuning Recommendation

## Purpose

This document captures the current recommendation for whether `{train}` should adopt an offline
fine-tuning lane, and if so, which ecosystem tools fit the platform best.

It is not a commitment to immediate implementation.
It is the decision record and adoption shape future work should follow.

## Decision Summary

`{train}` should treat offline fine-tuning as a bounded future capability, not as the center of the
platform.

Current recommendation:

- use `QLoRA` as the default parameter-efficient fine-tuning method
- keep the active delivery plan Apple-Silicon-only
- use `mlx-lm` as the first active local fine-tuning path
- keep `Ollama` as a local adapter-serving target, not as the primary training framework
- do not include `Unsloth`, `Axolotl`, or `LLaMA-Factory` in the active delivery plan right now

## Why This Fits `{train}`

`{train}` is an offline bounded optimizer.

That means any fine-tuning lane must preserve these rules:

- `{train}` consumes explicit datasets, traces, and review artifacts
- `{train}` emits explicit versioned proposal artifacts
- `{train}` must not mutate live `{trinity}` runtime behavior directly
- training outputs must remain replayable, reviewable, and promotion-gated

An offline adapter-training lane can fit the platform if it stays on the optimizer side of the
boundary:

- input: exported corpora, dataset slices, grader suites, skeptical reviews, and explicit training specs
- output: one versioned adapter package plus eval evidence and promotion metadata

## Tool Assessment

### `QLoRA`

Best viewed as the default method, not the framework.

Why it matters:

- it is the clearest cost-reduction lever for bounded fine-tuning
- it keeps GPU memory demands far lower than full fine-tuning
- it is already the common efficient path across the surrounding open-source ecosystem

For `{train}`, `QLoRA` is the right default if the goal is:

- cheap offline teaching from accepted datasets
- bounded preference optimization from reviewed comparison artifacts
- local-first experimentation without requiring large GPU fleets

### `mlx-lm`

Best first active implementation path for an Apple-Silicon-only lane.

Why it fits first:

- official Apple Silicon support
- explicit `LoRA` and `QLoRA` fine-tuning support in the `mlx_lm.lora` workflow
- local command-line path for train, test, and generate
- good fit for a narrow first worker that consumes governed datasets and emits adapter artifacts

For `{train}`, `mlx-lm` is the correct phase-one worker because it can support:

- supervised adapter training from registered datasets
- quantized adapter training on Apple Silicon
- a local-first worker without depending on ecosystems still framing Apple Silicon training support as in progress

### `Unsloth`

Useful research input, but not part of the active plan.

Do not count it in active delivery planning until its Apple Silicon / MLX training story is no longer documented as in progress.

### `LLaMA-Factory`

Useful, but not part of the active plan.

Its main advantages are:

- broad model coverage
- zero-code CLI and Web UI workflow
- convenient dataset configuration and evaluation surfaces

That is valuable only if `{train}` decides it needs a human-operated training console.

Today the repo is closer to:

- dataset registry
- grader suites
- explicit replay and review artifacts
- automation-first bounded optimization

So `LLaMA-Factory` should stay out of the current delivery lane.

### `Axolotl`

Also out of the active plan for now.

It remains more relevant to larger GPU-oriented training operations than to the current Apple-Silicon-only local system.

### `Ollama + LoRA`

Useful as a serving and packaging path, not as the main training stack.

`Ollama` already fits `{train}` as a provider adapter and can remain the local runtime target for
accepted adapters.

But the actual fine-tuning work should happen in a training framework that then emits adapter
artifacts which can be loaded into `Ollama`.

## Recommended Adoption Shape

If `{train}` adopts this lane, the first implementation should be:

1. one offline training worker that consumes a registered dataset version or saved slice
2. one explicit training spec artifact that declares:
   - base model
   - method (`qlora`, later `lora` or `dpo`)
   - hyperparameters
   - target proposal family or adapter family
   - expected output paths
3. one bounded execution path that produces:
   - adapter artifact
   - training report
   - eval report against an attached grader suite
   - promotion-ready metadata
4. one explicit optional packaging step for local `Ollama` use

That first lane should use:

- `QLoRA`
- `mlx-lm`
- local filesystem artifacts
- existing dataset registry and grader-suite registry

It should not start with:

- full fine-tuning
- distributed training
- human UI-first workflows
- direct runtime promotion

## Annotation Implications

These tools do not replace annotation or review discipline.

They help consume:

- supervised examples
- chosen/rejected preference pairs
- reward or review signals

They do not solve:

- corpus curation
- tenant isolation
- evidence review
- skeptical approval
- policy promotion governance

`{train}` should continue to treat dataset registry, grader suites, and skeptical review artifacts
as the real quality-control backbone.

## Recommended First Issue

The right first implementation issue is:

- add one offline fine-tuning worker lane that trains `QLoRA` adapters from registered datasets and
  evaluates them with persistent grader suites

Phase-one framework choice:

- `mlx-lm`

## Sources

- [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314)
- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
- [MLX LM](https://github.com/ml-explore/mlx-lm)
- [MLX LM LoRA / QLoRA Guide](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md)
- [Unsloth Docs](https://unsloth.ai/docs)
- [Unsloth Installation](https://docs.unsloth.ai/get-started/install-and-update)
- [Ollama Modelfile Reference](https://docs.ollama.com/modelfile)
- [Ollama Importing Adapters](https://docs.ollama.com/import)
