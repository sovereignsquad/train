# {reply} Draft Benchmark Hypothesis

## Component Under Optimization

- mutable artifact: `projects/reply/train.py`
- scope: bounded draft scoring logic for the starter `{reply}` fixture lane

## Hypothesis

Sharper reply scoring and selection rules should increase draft quality on fixed `{reply}` fixtures by rewarding concise, relevant, style-aligned proposals without broadening into live runtime behavior.

## Expected Metric Movement

- metric: `draft_score`
- expected direction: increase

## Failure Meaning

If `draft_score` does not improve, the candidate likely optimized the wrong signal, overfit a narrow fixture artifact, or introduced scoring logic that does not reflect useful reply quality.
