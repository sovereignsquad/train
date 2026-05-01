# Helpdesk Benchmark

This is the second reference benchmark for `autotrain`.

Purpose:

- validate that the platform works for a non-language-model project shape
- provide one controlled mutable artifact
- provide one bounded execution entrypoint
- provide one machine-readable metric payload
- stress a maximize-metric workflow instead of a minimize-metric workflow

Current benchmark contract:

- mutable artifact: `projects/helpdesk/train.py`
- entrypoint: `projects/helpdesk/run_benchmark.py`
- metric: `macro_f1`
- direction: higher is better

Rules:

1. Only modify `projects/helpdesk/train.py`.
2. Do not modify the platform code, dependencies, prompts, or benchmark data files.
3. Prefer one small, honest change over multiple speculative changes.
4. Keep the benchmark deterministic and local.
5. Validate ideas by running the benchmark entrypoint locally before stopping.

Recommended experiment directions:

- tune keyword boosts and priors
- tune token normalization behavior
- improve label discrimination without adding complexity

Forbidden:

- adding packages
- modifying `prepare.py`
- modifying `run_benchmark.py`
- editing files outside the declared mutable artifact

Execution note:

When running autonomously, do one bounded experiment cycle and leave the repository state aligned with the measured result.
