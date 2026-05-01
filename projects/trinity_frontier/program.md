# {trinity} Frontier Benchmark

This project lets `{train}` optimize a bounded `{trinity}` component without taking over runtime ownership.

Purpose:

- optimize the frontier-ranking heuristic used by `{trinity}`
- keep the mutable artifact narrow and deterministic
- score only the ranking quality of a small candidate pool
- prove the `{train}` to `{trinity}` integration path on a bounded artifact

Current contract:

- mutable artifact: `projects/trinity_frontier/train.py`
- entrypoint: `projects/trinity_frontier/run_benchmark.py`
- metric: `ranking_score`
- direction: higher is better

Rules:

1. Only modify `projects/trinity_frontier/train.py`.
2. Do not modify the benchmark entrypoint, fixture, or setup file during autonomous runs.
3. Keep the ranking output deterministic.
4. Treat the committed fixture as a bounded starter benchmark, not a production policy.
5. Runtime orchestration remains in `{trinity}`. This project optimizes only the ranking function.
