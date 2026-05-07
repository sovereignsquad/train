# Mythology Benchmark Hypothesis

## Component Under Optimization

- mutable artifact: `projects/mythology/train.py`
- scope: n-gram language-model behavior for the bounded mythology benchmark

## Hypothesis

Small changes to smoothing, token normalization, or n-gram handling can reduce validation bits-per-byte without expanding the benchmark boundary or adding external dependencies.

## Expected Metric Movement

- metric: `val_bpb`
- expected direction: decrease

## Failure Meaning

If the metric does not improve, the candidate likely targeted a weak lever, overfit the tiny corpus shape, or increased complexity without reducing language-model error.
