# {trinity} Frontier Promotion Contract

## Purpose

This document defines how a bounded `{train}` result for the `{trinity}` frontier benchmark maps back into `{trinity}` without mixing repository ownership.

## Promotion Rules

1. `{train}` may optimize only the benchmark artifact in `projects/trinity_frontier/train.py`.
2. The promoted output is the ranking heuristic itself:
   - weight values
   - deterministic ranking formula
   - documented score semantics
3. `{train}` must not promote:
   - product-facing UI changes
   - channel routing behavior
   - `{reply}` orchestration logic
   - unbounded runtime code changes

## Import Path

When `{trinity}` is ready to consume optimized frontier policies:

1. copy the approved scoring parameters or formula from the accepted `{train}` artifact
2. re-express them inside `{trinity}` runtime-owned code
3. run `{trinity}` unit and contract tests
4. validate the effect in `{reply}` shadow mode before default cutover

## Governance

- `{train}` proposes an improvement.
- `{trinity}` owns the runtime implementation of that improvement.
- `{reply}` validates downstream operator behavior but does not define the ranking contract.
