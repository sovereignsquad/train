# Mythology Benchmark

This is the first reference benchmark for `autotrain`.

Purpose:

- prove the general-purpose platform contract
- provide one controlled mutable artifact
- provide one bounded execution entrypoint
- provide one machine-readable metric payload

Current benchmark contract:

- mutable artifact: `projects/mythology/train.py`
- entrypoint: `projects/mythology/run_benchmark.py`
- metric: `val_bpb`
- direction: lower is better

Rules:

1. Only modify `projects/mythology/train.py`.
2. Do not modify the platform code, dependencies, prompts, or benchmark data files.
3. Prefer one small, honest change over multiple speculative changes.
4. Keep the benchmark deterministic and local.
5. Validate ideas by running the benchmark entrypoint locally before stopping.

Recommended experiment directions:

- tune `NGRAM_ORDER`
- tune `ADD_K_SMOOTHING`
- tune text normalization behavior if it improves `val_bpb`
- keep model simplicity unless a change clearly improves the metric

Forbidden:

- adding packages
- modifying `prepare.py`
- modifying `run_benchmark.py`
- editing files outside the declared mutable artifact

Execution note:

When running autonomously, do one bounded experiment cycle and leave the repository state aligned with the measured result.
