# Train Execution Backlog

## Objective

Deliver the `{train}` portion of the cross-project boundary program without mixing repository ownership.

`{train}` remains responsible for bounded optimization only. It must not absorb `{reply}` product orchestration or `{trinity}` runtime ownership.

## Milestones

### M1. Foundation Hardening

- [x] Restore repo-local Vibe runtime-home behavior under `artifacts/local/vibe-home`.
- [x] Record the execution backlog and issue queue in-repo.
- [ ] Verify clean local test, lint, and app-build baseline after changes.

### M2. Trinity Component Optimization Path

- [x] Add a bounded reference benchmark for the `{trinity}` frontier-ranking component.
- [ ] Add more runtime-component templates once `{trinity}` exports additional bounded artifacts.

### M3. Promotion Readiness

- [x] Add artifact-promotion notes for importing optimized ranking policies back into `{trinity}`.
- [ ] Add stronger regression fixtures once `{reply}` starts consuming Trinity frontier outputs.

## Active Issue Queue

### Closed

- `TRAIN-001` Repo-local Vibe runtime-home regression
  The status surface resolved `runtime_home` to `~/Library/Application Support/train/vibe-home` instead of the repo-local contract path expected by tests and by local operator workflows. Fixed by restoring the default to `artifacts/local/vibe-home`.

- `TRAIN-002` Missing first-class Trinity runtime benchmark
  The repository described bounded external runtime optimization but did not ship a concrete `{trinity}` reference benchmark. Fixed by adding `projects/trinity_frontier`.

- `TRAIN-003` Missing promotion contract for `{train}` to `{trinity}`
  The benchmark existed after implementation, but the repo still needed an explicit promotion rule for how optimized ranking artifacts map back into Trinity-owned code. Fixed by adding `docs/TRINITY_FRONTIER_PROMOTION.md`.

## Dependencies

- Depends on `{trinity}` to define stable bounded artifacts for runtime components.
- Independent of `{reply}` product orchestration, except where `{reply}` provides offline evaluation fixtures for future benchmarks.
