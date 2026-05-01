# Trinity Reply Trace Contract

## Purpose

`train` consumes exported Trinity reply traces as replay fixtures only. This does not authorize direct runtime ownership.

## Current Scope

1. validate `contract_version`
2. load `AcceptedArtifactVersion`
3. inspect `frontier_candidate_ids`
4. inspect `feedback_events`
5. replay bounded ranker logic against committed fixtures
6. optionally merge Reply shadow-comparison logs into generated fixtures

## Non-Goals

- no direct Reply database access
- no live product optimization
- no mutation of Trinity runtime code from Train

## Initial Deliverable Issues

1. add trace loader schema
2. add `trinity_reply_ranker` scaffold project
3. keep benchmark deterministic and fixture-bound
4. refuse malformed or incompatible trace exports
5. add a fixture-builder path from real Trinity exports and Reply shadow logs
