# {train} Execution Backlog

## Objective

Deliver the `{train}` portion of the cross-project boundary program without mixing repository ownership.

`{train}` remains responsible for bounded optimization only. It must not absorb `{reply}` product orchestration or `{trinity}` runtime ownership.

## Milestones

### M1. Foundation Hardening

- [x] Restore repo-local Vibe runtime-home behavior under `artifacts/local/vibe-home`.
- [x] Record the execution backlog and issue queue in-repo.
- [ ] Verify clean local test, lint, and app-build baseline after changes.

### M2. {trinity} Component Optimization Path

- [x] Add a bounded reference benchmark for the `{trinity}` frontier-ranking component.
- [ ] Add more runtime-component templates once `{trinity}` exports additional bounded artifacts.

### M3. Promotion Readiness

- [x] Add artifact-promotion notes for importing optimized ranking policies back into `{trinity}`.
- [ ] Add stronger regression fixtures once `{reply}` starts consuming `{trinity}` frontier outputs.

## Active Issue Queue

### Closed

- `TRAIN-001` Repo-local Vibe runtime-home regression
  The status surface resolved `runtime_home` to `~/Library/Application Support/train/vibe-home` instead of the repo-local contract path expected by tests and by local operator workflows. Fixed by restoring the default to `artifacts/local/vibe-home`.

- `TRAIN-002` Missing first-class `{trinity}` runtime benchmark
  The repository described bounded external runtime optimization but did not ship a concrete `{trinity}` reference benchmark. Fixed by adding `projects/trinity_frontier`.

- `TRAIN-003` Missing promotion contract for `{train}` to `{trinity}`
  The benchmark existed after implementation, but the repo still needed an explicit promotion rule for how optimized ranking artifacts map back into `{trinity}`-owned code. Fixed by adding `docs/TRINITY_FRONTIER_PROMOTION.md`.

- `TRAIN-POLICY-001` Training bundle loader
  The policy loop plan required `{train}` to consume bounded `{trinity}` learning bundles safely, but the repo only had a narrower trace loader. Fixed by extending the Trinity ingestion schemas with a validated training-bundle record, adding `load_trinity_training_bundle()` and directory loading helpers, and covering accepted, invalid-contract, and missing-candidate cases in tests.

- `TRAIN-POLICY-002` Tone learner
  The bundle loader established the input boundary, but `{train}` still had no first bounded learner that could turn exported operator outcomes into a candidate reply behavior artifact. Fixed by adding `core/train_core/trinity_tone_learner.py`, extending `core/train_core/schemas.py` with a versioned `ReplyBehaviorPolicyProposal` shape, and covering channel-scoped, global-scope, and invalid-bundle cases in tests.

- `TRAIN-POLICY-003` Brevity learner
  `{train}` could now learn tone, but it still lacked the bounded brevity slice needed to reduce operator rewrite severity caused by length mismatch. Fixed by adding `core/train_core/trinity_brevity_learner.py`, deriving deterministic brevity constraints from `brevity-learning` bundles, and covering channel-scoped, global-scope, and invalid-bundle cases in tests.

- `TRAIN-POLICY-004` Channel formatting learner
  `{train}` still lacked the bounded formatting slice for channel-specific presentation rules such as openings, URL handling, attachment mentions, and newline density. Fixed by adding `core/train_core/trinity_channel_formatting_learner.py`, deriving deterministic formatting rules from `channel-formatting-learning` bundles, and covering channel-scoped, global-scope, and invalid-bundle cases in tests.

- `TRAIN-POLICY-005` Proposal artifact and eval report
  The individual learners could emit candidate policy proposals, but `{train}` still lacked a deterministic report surface that packaged a candidate proposal alongside incumbent provenance and replay-corpus summary metrics. Fixed by adding `core/train_core/trinity_policy_eval.py`, defining a versioned replay-ready eval report shape, and covering incumbent-vs-candidate report generation in tests.

### Open

- `TRAIN-004` Web toolchain major-version upgrade lane
  `apps/web` is clean on lint, production build, and audit after safe updates, but major upgrades remain for `eslint` and `typescript`. Those should be handled as a dedicated compatibility lane against the Next 16 toolchain.

- `TRAIN-BRAIN-001` Bounded ranking-policy learner for richer Trinity runtime exports
  The live-brain direction may eventually let `{trinity}` export bounded ranking-policy artifacts, but `{train}` must only learn from explicit exported artifact families and must not infer live runtime ownership from this.

- `TRAIN-BRAIN-002` Bounded retrieval-selection learner for richer Trinity runtime exports
  If `{trinity}` later exports replayable retrieval traces, `{train}` may optimize retrieval-selection policy proposals offline without becoming the live retrieval owner.

- `TRAIN-BRAIN-003` Skeptical eval lane for prepared-draft and retrieval proposals
  Brain-adjacent runtime artifacts will require stronger minority-report and skeptical-eval coverage before promotion back into `{trinity}`.

## Dependencies

- Depends on `{trinity}` to define stable bounded artifacts for runtime components.
- Independent of `{reply}` product orchestration, except where `{reply}` provides offline evaluation fixtures for future benchmarks.
