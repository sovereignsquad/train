# Helpdesk Benchmark Hypothesis

## Component Under Optimization

- mutable artifact: `projects/helpdesk/train.py`
- scope: deterministic helpdesk intent scoring and label discrimination

## Hypothesis

Refining keyword weighting, normalization, or class-prior handling should improve classification quality on the fixed benchmark without changing the benchmark contract.

## Expected Metric Movement

- metric: `macro_f1`
- expected direction: increase

## Failure Meaning

If `macro_f1` does not improve, the candidate likely tuned the wrong heuristic, overfit a narrow intent pattern, or added complexity that does not improve class separation.
