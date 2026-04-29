# Recovery

## Purpose

This document defines the current recovery and rollback behavior for the local ratchet flow.

## Current Ratchet Mutation Policy

The ratchet is currently allowed to mutate git state only under strict constraints.

Allowed:

- commit the declared mutable artifact when a run is accepted
- restore the declared mutable artifact when a run is rejected

Not allowed:

- commit arbitrary files
- restore arbitrary files
- mutate the repo when files outside the mutable artifact are dirty

## Fail-Closed Rule

If the git worktree contains changes outside the declared mutable artifact:

- ratchet mutation is blocked
- the run remains recorded
- manual cleanup is required before retrying

This is intentional.

## Current Safety Boundary

Today the mutable artifact for the first benchmark is:

- `projects/mythology/train.py`

The ratchet should not mutate anything else automatically.

## Recovery Guidance

If ratchet mutation is blocked:

1. inspect `git status`
2. clean or commit unrelated changes manually
3. ensure only the declared mutable artifact is dirty
4. re-run the ratchet step if appropriate

## Current Limitation

The ratchet currently performs:

- accepted-run commit
- rejected-run restore

It does not yet perform:

- multi-file transactional restores
- branch management
- advanced rollback orchestration
- migration-aware recovery
