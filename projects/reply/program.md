# {reply} Draft Benchmark

This is the first `{trinity}`-style reference project for `{train}`.

Purpose:

- prove that `train` can optimize a bounded reply-drafting component
- keep the mutable artifact narrow and local
- use one automatic maximize metric
- stay compatible with later runtime integration work such as `{trinity}`

Current contract:

- mutable artifact: `projects/reply/train.py`
- entrypoint: `projects/reply/run_benchmark.py`
- metric: `draft_score`
- direction: higher is better

Rules:

1. Only modify `projects/reply/train.py`.
2. Do not modify the benchmark entrypoint, fixtures, or setup file during autonomous runs.
3. Keep the output deterministic.
4. Treat the committed fixture as a starter benchmark only.
5. Real private message history belongs under local-only artifacts, not git.

Execution note:

The benchmark uses `<TRAIN_STATE_DIR>/reply/eval.json` when present. Otherwise it falls back to the committed fixture in this project.
