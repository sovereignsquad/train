# {trinity} {reply} Ranker Trace Replay Hypothesis

## Component Under Optimization

- mutable artifact: `projects/trinity_reply_ranker/train.py`
- scope: replay-time ranking alignment over exported `{trinity}` `{reply}` traces

## Hypothesis

A better bounded ranking policy should improve alignment with the fixed replay fixtures by surfacing candidates that more closely match the accepted trace outcomes without pretending live runtime optimization is already solved.

## Expected Metric Movement

- metric: `trace_alignment_score`
- expected direction: increase

## Failure Meaning

If the score does not improve, the candidate likely targeted fixture noise, missed the real alignment signal, or relied on heuristics that do not generalize beyond the replay scaffold.
