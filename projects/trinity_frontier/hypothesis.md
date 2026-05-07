# {trinity} Frontier Benchmark Hypothesis

## Component Under Optimization

- mutable artifact: `projects/trinity_frontier/train.py`
- scope: frontier ranking behavior over a bounded `{trinity}` candidate pool

## Hypothesis

Improving the frontier ranking heuristic should raise the benchmark score by promoting candidates that better match the fixed desired ordering without taking over `{trinity}` runtime orchestration.

## Expected Metric Movement

- metric: `ranking_score`
- expected direction: increase

## Failure Meaning

If the metric does not improve, the ranking heuristic likely emphasized weak features, overfit fixture-specific ordering quirks, or failed to target the real selection bottleneck.
