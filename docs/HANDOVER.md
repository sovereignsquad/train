# Handover

## Purpose

This is the current resume document for `{train}`.

## Current Handover

### What Changed Last

Last meaningful tranche:

- repo now contains an explicit optimizer-boundary document for the future `{reply}` live-brain system
- `{train}` became the bounded offline consumer of `{trinity}` Reply adapter training bundles
- `{train}` now exposes a first-class proposal surface that `{trinity}` can call by API or CLI
- `{train}` now also consumes bounded Spot training bundles for the first review-policy slice and can emit proposal/eval/comparison artifacts by API or CLI for Trinity adoption
- Spot review-policy proposals now carry explicit scope, so one-company corpora emit company-scoped artifacts that Trinity can adopt without cross-tenant leakage
- open-source docs and comment guidance were tightened so README, setup, boundary docs, coding standards, and handover/status files describe the same bounded Reply-plus-Spot reality
- the ranking-learning export contract required before future Trinity ranking-policy learner work is now defined explicitly in-repo
- the retrieval-selection export contract required before future Trinity retrieval learner work is now defined explicitly in-repo
- the skeptical-eval report contract required before broader brain-adjacent review work is now defined explicitly in-repo
- the first bounded skeptical-eval implementation lane now exists in code, API, CLI, and tests for higher-risk proposal review
- the first bounded eval dataset registry now exists in code, API, dataset/slice persistence, and tests so proposal lanes can reuse corpora instead of raw file lists
- the first bounded persistent grader-suite layer now exists in code, API, CLI, and tests so datasets can carry reusable evaluation criteria across proposal variants
- the first bounded hybrid evaluator layer now exists in code, API, CLI, and tests so one replayable run can combine code evaluators with imported model and human review artifacts
- the repo now contains a research-backed offline fine-tuning recommendation that keeps the active delivery plan Apple-Silicon-only, uses `QLoRA` as the method, treats `mlx-lm` as the first active worker path, and keeps `Ollama` as a serving target rather than the main training stack
- the repo now also contains an implementation-facing self-learning system design that spells out the daily offline loop: trace capture, corpus building, `mlx-lm` `QLoRA` training, grader-suite evaluation, skeptical review, optional Ollama packaging, and controlled adoption
- the first offline training-spec and adapter-artifact contract layer now exists in code, migration, API, docs, and tests, with backend-aware but Apple-Silicon-compatible contract values for the future `mlx-lm` worker path
- the first Apple-Silicon `mlx-lm` worker lane now exists in code, API, CLI, docs, and tests, including dataset partition export into `mlx-lm` layout, subprocess launch, log capture, metadata capture, and adapter-artifact persistence
- the repo now also contains a model storage audit and centralization plan in `docs/MODEL_STORAGE_AUDIT.md` that defines `/Users/Shared/Models` as the target machine-level local asset root without collapsing provider adapters into filesystem logic
- the repo now also has a first model-root contract in code and docs through `TRAIN_MODELS_ROOT` plus `train_core.model_resolution`, so future local model work can resolve governed relative refs safely before registry or UI work starts
- the offline training-spec and adapter-artifact contracts now also persist `base_model_source_kind`, and `mlx-lm` specs now reject `ollama` base-model refs while resolving governed local-path refs through `TRAIN_MODELS_ROOT`
- the repo now also contains a dedicated integration dependency/reference inventory and local health-audit snapshot in `docs/INTEGRATION_SURFACE.md`
- the integration-hardening follow-up is now decomposed into GitHub issues `#66`-`#70`, with dependencies updated on `#1`, `#61`, `#64`, and `#65`, and board statuses aligned to the recommended delivery order
- the hardening tranche now also has working code for relation doctor checks, offline training readiness checks, live operator-client smoke coverage, a live cross-repo `{trinity}` handoff proof, deterministic Ollama packaging, and one bounded daily self-learning cycle entrypoint
- those hardening surfaces are now exposed through both CLI and API, and the macOS updater relation now has a dedicated packaged-release preflight script
- the operational follow-through on `2026-05-20` closed the two main runtime gaps from the previous audit: `mlx-lm` is now installed on the audited machine, and GitHub Releases now serves published release `v0.1.0` with attached macOS app assets

Implemented or now present in the active working tree:

- `docs/TRINITY_LIVE_BRAIN_OPTIMIZATION_BOUNDARY.md`
- Trinity training-bundle ingestion schemas
- trace and bundle loader helpers
- bounded tone learner
- bounded brevity learner
- bounded channel-formatting learner
- reply policy eval report builder
- reply policy proposal service from bundle files
- `/v1/trinity/reply/policies/propose` endpoint
- `python -m train_core.cli propose-reply-policy` CLI surface
- company-aware scope inference so one-company corpora do not collapse into channel-wide proposals
- first-class `hypothesis.md` contract plus project/bootstrap support
- standard comparison harness for baseline/incumbent/candidate policy reporting
- docs aligned around the `{reply}` / `{trinity}` / `{train}` operating split
- docs and inline comment standards now explicitly require public documentation to stay aligned with shipped behavior
- `docs/TRINITY_RANKING_LEARNING_EXPORT_CONTRACT.md`
- `docs/TRINITY_RETRIEVAL_SELECTION_EXPORT_CONTRACT.md`
- `docs/TRINITY_SKEPTICAL_EVAL_REPORT_CONTRACT.md`
- `docs/EVAL_DATASET_REGISTRY.md`
- `docs/PERSISTENT_GRADER_SUITES.md`
- `docs/HYBRID_EVALUATORS.md`
- `docs/OFFLINE_FINE_TUNING_RECOMMENDATION.md`
- `docs/OFFLINE_TRAINING_CONTRACTS.md`
- `docs/SELF_LEARNING_FINE_TUNING_SYSTEM.md`
- offline fine-tuning contract service and persistence layer
- `/v1/training-specs` endpoints
- `/v1/adapter-artifacts` endpoints
- `mlx-lm` worker runner from persisted training specs
- `/v1/training-specs/{spec_key}/versions/{spec_version}/runs` endpoint
- `/v1/doctor` endpoint
- `/v1/training-specs/{spec_key}/versions/{spec_version}/readiness` endpoint
- `/v1/adapter-artifacts/{artifact_key}/versions/{artifact_version}/ollama-package` endpoint
- `/v1/training-specs/{spec_key}/versions/{spec_version}/self-learning-cycle` endpoint
- `python -m train_core.cli run-training-spec` CLI surface
- `python -m train_core.cli doctor` CLI surface
- `python -m train_core.cli check-training-readiness` CLI surface
- `python -m train_core.cli package-adapter-artifact-for-ollama` CLI surface
- `python -m train_core.cli run-daily-self-learning-cycle` CLI surface
- eval dataset registry service and dataset-slice resolver
- `/v1/eval-datasets` dataset registry endpoints
- persistent grader-suite registry and rerun service
- `/v1/eval-datasets/.../grader-suites` endpoints
- hybrid evaluator artifact import path and disagreement reporting
- skeptical-eval report builder from comparison artifacts
- `/v1/trinity/reviews/skeptical-eval` endpoint
- `python -m train_core.cli build-skeptical-eval-report` CLI surface
- Spot review-policy proposal service from bundle files
- `/v1/trinity/spot/policies/propose` endpoint
- `python -m train_core.cli propose-spot-review-policy` CLI surface
- `scripts/check_operator_clients.py`
- `scripts/prove_trinity_train_handoff.py`
- `scripts/check_packaged_release_contract.py`
- published GitHub release `v0.1.0`

### What Was Verified

Verified:

- `uv run pytest`
- `uv run ruff check .`
- targeted Spot and Reply proposal tests after the documentation consistency pass
- ranking-export contract documentation pass for issue `#33`
- retrieval-export contract documentation pass for issue `#34`
- skeptical-eval report contract documentation pass for issue `#35`
- targeted skeptical-eval implementation tests for issue `#32`
- targeted eval dataset registry implementation tests for issue `#36`
- targeted persistent grader-suite implementation tests for issue `#37`
- targeted hybrid evaluator implementation tests for issue `#38`
- documentation review for the offline fine-tuning adoption recommendation
- documentation review for the self-learning fine-tuning system design
- targeted offline fine-tuning contract tests
- targeted `mlx-lm` worker tests
- targeted model-root config and model-resolution tests
- targeted training-spec model-source-kind validation tests
- targeted doctor, training-readiness, Ollama packaging, and bounded self-learning cycle tests
- local integration audit on `2026-05-19` covering API smoke, agent/provider status, web build, macOS build, GitHub release reachability, and bounded `{trinity}` seam tests
- operational verification on `2026-05-20` covering `uv sync --extra dev --extra local-training`, successful training doctor checks, successful packaged release preflight, and uploaded macOS release assets for `v0.1.0`

### What Needs To Happen Next

1. decide whether `{train}` should own supervised API startup helpers or remain API-server passive
2. decide whether the next platform lane should widen runtime-facing learners or extend evaluator execution beyond imported artifacts
3. keep the Reply-adapter policy lane reproducible and bounded
4. avoid direct runtime mutation paths
5. do not let ecosystem inspiration turn `{train}` into a prompt framework
6. keep the Spot lane bounded to review-policy until Trinity has company-scoped Spot adoption and broader Spot artifact contracts
7. keep README, coding standards, setup, boundary docs, and handover/status docs in sync whenever bounded capability scope changes
8. do not start `#30` implementation until real `{trinity}` exports satisfy the ranking-learning contract document
9. do not start `#31` implementation until real `{trinity}` exports satisfy the retrieval-selection contract document
10. if a new offline fine-tuning lane is started, keep it offline-only and artifact-governed; do not let training outputs bypass dataset, eval, or promotion discipline
11. do not call the future training lane “automatic self-improvement” unless the docs still make the offline review and promotion gates explicit
12. keep the new training-spec and adapter-artifact contracts backend-neutral enough for `mlx-lm`, but do not widen them into speculative multi-backend orchestration before the first adapter-evaluation lane exists
13. if model-root work starts next, add `TRAIN_MODELS_ROOT` plus path resolution first; do not jump straight to provider, UI, or packaging changes without a storage contract
14. next model-root increments should tighten training-spec validation and add local inventory; do not spread direct path handling across workers or UI code
15. keep local-path resolution centralized in `train_core.model_resolution`; do not duplicate root-joining logic in schemas, workers, API routes, or UI code
16. keep the new doctor and training-readiness surfaces honest as relations widen; do not let them degrade into shallow connectivity checks
17. keep the live `{trinity}` proof runnable from local sibling checkouts; do not replace it with doc-only or mocked proofs
18. use issue `#1` as the roadmap anchor for the remaining hardening and automation order after the current tranche: deeper `#64`, more robust `#69`, then scheduling and governance completion for `#65`

### Watch Carefully

- do not let `{train}` absorb live runtime behavior from `{trinity}`
- do not let proposal artifacts become implicit side effects
- keep policy provenance explicit and single-source
- keep replay corpora stable enough to support incumbent-vs-candidate evaluation
- do not regress company scope back to channel-only inference, or the Trinity isolation work will be undermined
- borrow eval rigor and optimization framing, but resist prompt-framework drift
- do not let future “brain” language blur the ownership line: `{train}` improves exported artifacts, `{trinity}` remains the live runtime
- do not overstate the current Spot support: `{train}` now has a first bounded Spot proposal/eval lane, not a broad Spot optimizer surface
- do not drop the new scope discipline: one-company Spot corpora must stay company-scoped unless Trinity’s adoption contract is intentionally widened later
- do not let public docs drift back to Reply-only wording while dataset-registry, grader-suite, hybrid-evaluator, Spot, and skeptical-review support are present in the shipped repo
- do not let ecosystem training tools pull `{train}` into UI-first training management or direct runtime mutation; the first acceptable shape is a bounded offline worker fed by registered datasets and grader suites
- do not let the active plan drift back toward `Unsloth`, `Axolotl`, or `LLaMA-Factory` while the actual local delivery target remains Apple Silicon
- do not skip holdout, disagreement, or promotion evidence in the name of daily learning speed; the system should improve day by day because it learns more honestly, not because it updates more recklessly
