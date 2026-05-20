# Status

## Purpose

This is the current status document for `{train}`.

## Current Phase

Phase:

- bounded optimizer role clarified
- Reply-adapter policy bundle consumer lane implemented
- tone, brevity, and channel-formatting proposal surfaces added
- incumbent-vs-candidate reply policy eval reporting added
- Trinity-callable Reply policy proposal API and CLI added
- first-class `hypothesis.md` contract added for serious `{train}` projects
- standard comparison harness added for the Trinity Reply policy seam

Primary active lane:

- keep the Reply-adapter optimization loop explicit and reproducible rather than broadening into hidden runtime mutation
- document and preserve the optimizer boundary as `{trinity}` grows toward a fuller live-brain runtime
- add bounded non-Reply artifact families only when `{trinity}` exports and promotion seams are explicit enough to keep adoption governed

## Current Reality

The repository currently has:

- Python platform scaffold
- FastAPI local API
- native macOS shell
- web operator UI
- project registry and run lifecycle
- eval dataset registry with versioned corpora and saved slices
- persistent grader-suite registry attached to datasets and proposal families
- hybrid evaluator replay support for code, model-judge, and human-review inputs
- provider registry and operator recovery
- reference benchmark projects
- `{trinity}` trace and training-bundle ingestion models
- bounded Reply-adapter tone learner
- bounded Reply-adapter brevity learner
- bounded Reply-adapter channel-formatting learner
- Reply-adapter policy eval report builder
- `/v1/trinity/reply/policies/propose` API endpoint
- `python -m train_core.cli propose-reply-policy` CLI entrypoint
- company-aware scope inference for Reply policy proposals
- fixed-shape baseline/incumbent/candidate comparison reporting for Reply policy proposals
- repo-resident optimizer-boundary spec for the live-brain direction in `docs/TRINITY_LIVE_BRAIN_OPTIMIZATION_BOUNDARY.md`
- repo-resident ranking-learning export contract spec for the future `{trinity}` ranking-family seam in `docs/TRINITY_RANKING_LEARNING_EXPORT_CONTRACT.md`
- repo-resident retrieval-selection export contract spec for the future `{trinity}` retrieval-family seam in `docs/TRINITY_RETRIEVAL_SELECTION_EXPORT_CONTRACT.md`
- repo-resident skeptical-eval report contract spec for higher-risk proposal review in `docs/TRINITY_SKEPTICAL_EVAL_REPORT_CONTRACT.md`
- first bounded skeptical-eval report builder for higher-risk proposal review
- `POST /v1/trinity/reviews/skeptical-eval` API endpoint
- `python -m train_core.cli build-skeptical-eval-report` CLI entrypoint
- `POST /v1/eval-datasets` API endpoint
- `POST /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/slices` API endpoint
- `POST /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/grader-suites` API endpoint
- `POST /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/grader-suites/{suite_key}/versions/{suite_version}/runs` API endpoint
- `python -m train_core.cli run-grader-suite` CLI entrypoint
- offline fine-tuning training-spec contract persistence and API surface
- offline fine-tuning adapter-artifact contract persistence and API surface
- `GET/POST/DELETE /v1/training-specs...` API endpoints
- `GET/POST/DELETE /v1/adapter-artifacts...` API endpoints
- first Apple-Silicon `mlx-lm` worker that exports governed dataset partitions and launches bounded `QLoRA` adapter training from persisted training specs
- training specs and adapter artifacts now persist `base_model_source_kind`, with local-path refs governed by `TRAIN_MODELS_ROOT`
- `POST /v1/training-specs/{spec_key}/versions/{spec_version}/runs` API endpoint
- `python -m train_core.cli run-training-spec` CLI entrypoint
- `TRAIN_MODELS_ROOT` environment contract and first local model-resolution helper
- `python -m train_core.cli doctor` CLI entrypoint for relation readiness
- `python -m train_core.cli check-training-readiness` CLI entrypoint for offline training readiness
- `python -m train_core.cli package-adapter-artifact-for-ollama` CLI entrypoint for deterministic local Ollama packaging
- `python -m train_core.cli run-daily-self-learning-cycle` CLI entrypoint for one bounded offline training-plus-eval-plus-packaging loop
- `GET /v1/doctor`, `GET /v1/training-specs/.../readiness`, `POST /v1/adapter-artifacts/.../ollama-package`, and `POST /v1/training-specs/.../self-learning-cycle` API endpoints
- `scripts/check_operator_clients.py` live API contract smoke for the shipped operator clients
- `scripts/prove_trinity_train_handoff.py` live cross-repo `{trinity}` to `{train}` handoff proof
- `scripts/check_packaged_release_contract.py` packaged macOS updater/release preflight
- first bounded Spot training-bundle consumer and review-policy learner/eval path
- `/v1/trinity/spot/policies/propose` API endpoint
- `python -m train_core.cli propose-spot-review-policy` CLI entrypoint
- Spot review-policy proposals now emit explicit scope, with one-company corpora producing company-scoped artifacts and multi-company corpora reserved for global artifacts
- repo-resident model storage audit and centralization plan in `docs/MODEL_STORAGE_AUDIT.md`
- repo-resident integration dependency/reference inventory and health audit in `docs/INTEGRATION_SURFACE.md`
- integration hardening delivery tranche mapped into GitHub issues `#66`-`#70` and synced to the `{train}` project board

## Verified Working

Verified locally in the current implementation lane:

- `uv run pytest`
- `uv run ruff check .`
- targeted Reply-adapter learner tests
- targeted Spot review-policy tests
- targeted skeptical-eval lane tests
- targeted eval dataset registry tests
- targeted persistent grader-suite tests
- targeted hybrid evaluator tests
- targeted offline fine-tuning contract and `mlx-lm` worker tests
- targeted model-root config and model-resolution tests
- targeted training-spec model-source-kind validation tests
- targeted doctor, training-readiness, Ollama packaging, and daily self-learning cycle tests
- Reply proof lane through `scripts/prove_reply_cycle.py`
- operator-client contract smoke through `scripts/check_operator_clients.py`
- live cross-repo handoff proof through `scripts/prove_trinity_train_handoff.py`
- packaged release preflight through `scripts/check_packaged_release_contract.py`
- integration audit checks on `2026-05-19` covering API smoke, agent/provider status, web build, macOS build, and bounded `{trinity}` seam tests
- operational closure on `2026-05-20` covering `mlx-lm` installation, successful training doctor checks, first published GitHub release `v0.1.0`, and attached macOS release assets

## Current Gaps

Still intentionally not owned by `{train}`:

- live runtime behavior
- product transport semantics
- direct artifact promotion into `{trinity}`
- fully unattended API-server lifecycle ownership from `{trinity}`; the server still needs to be running when API transport is selected

Still open:

- broader comparison harnesses and invariants beyond the first Reply-adapter slice
- longer unattended operator/runtime recovery exercises
- richer Trinity runtime artifact families have not been exported yet, so no ranking or retrieval learners should be added ahead of those contracts
- the ranking-learning export contract lane from GitHub issue `#33` is now defined in-repo
- the retrieval-selection export contract lane from GitHub issue `#34` is now defined in-repo
- the skeptical-eval report contract lane from GitHub issue `#35` is now defined in-repo
- the broader skeptical-eval implementation lane from GitHub issue `#32` is now implemented in a first bounded reusable form
- the eval dataset registry lane from GitHub issue `#36` is now implemented in a first bounded reusable form
- the persistent grader-suite lane from GitHub issue `#37` is now implemented in a first bounded reusable form
- the hybrid evaluator lane from GitHub issue `#38` is now implemented in a first bounded reusable form
- the offline training-spec and adapter-artifact contract lane from GitHub issue `#62` is now implemented in a first bounded reusable form
- the first Apple-Silicon `mlx-lm` worker lane from GitHub issue `#63` is now implemented in a first bounded reusable form
- Spot proposal/eval support is still only the first review-policy slice; no broader Spot threshold/routing/prompt artifact families are implemented yet
- Spot scope support is still intentionally narrow: only `company` and `global` are supported for the first review-policy slice
- public docs must keep describing the current bounded Reply-plus-Spot-plus-skeptical-review state accurately; do not let README or contributor docs drift backward
- the repo now has a research-backed recommendation for a future offline fine-tuning lane with an Apple-Silicon-only active plan centered on `mlx-lm`; the first contract layer and first worker path are now implemented, but no adapter-evaluation runner or promotion flow is implemented yet
- the repo now also has a first bounded daily offline self-learning cycle entrypoint, but no scheduler, no automatic corpus-building, and no automatic promotion path
- local model storage now has a first config, resolution, and training-spec validation contract around `/Users/Shared/Models`, but no registry or API inventory layer exists yet
- the offline training lane now has `mlx-lm` installed on the audited machine and exposes first-class readiness and doctor surfaces, but it remains environment-dependent across machines
- the macOS updater now has a live published release source and attached app assets, but the current macOS app artifact is ad-hoc signed and not notarized
- the recommended integration-hardening order is now explicit in issue `#1`: `#66`, `#68`, `#67`, `#64`, `#70`, `#69`, then `#65`

## Immediate Next Steps

1. keep the new Trinity-callable proposal seam stable and explicit
2. keep rejection-ready review artifacts explicit, versioned, and replayable as richer proposal families widen
3. decide whether to widen runtime-facing learner families or strengthen issue `#30` and `#31` once real `{trinity}` exports exist
4. keep proposal artifacts explicit and versioned
5. avoid turning `{train}` into a second runtime
6. avoid drifting into a generic prompt framework as the seam expands
7. keep live-brain memory and prepared-draft ownership out of `{train}` even if future artifact families widen
8. keep the new Spot learner slice bounded; do not let it imply live Spot runtime mutation or workbook ownership
9. if an offline fine-tuning lane is added, keep it bounded to explicit dataset inputs, explicit adapter outputs, and explicit eval/promotion artifacts
10. do not describe the system as automatically self-improving online; the intended shape is a governed daily offline loop with explicit promotion gates
11. keep the active delivery plan Apple-Silicon-only; do not treat `Unsloth`, `Axolotl`, or `LLaMA-Factory` as active backend commitments

## Resume Point

If resuming work, read:

1. [README.md](/Users/Shared/Projects/train/README.md)
2. [docs/STATUS.md](/Users/Shared/Projects/train/docs/STATUS.md)
3. [docs/HANDOVER.md](/Users/Shared/Projects/train/docs/HANDOVER.md)
4. [docs/SETUP.md](/Users/Shared/Projects/train/docs/SETUP.md)
5. [docs/OFFLINE_FINE_TUNING_RECOMMENDATION.md](/Users/Shared/Projects/train/docs/OFFLINE_FINE_TUNING_RECOMMENDATION.md)
6. [docs/OFFLINE_TRAINING_CONTRACTS.md](/Users/Shared/Projects/train/docs/OFFLINE_TRAINING_CONTRACTS.md)
7. [docs/SELF_LEARNING_FINE_TUNING_SYSTEM.md](/Users/Shared/Projects/train/docs/SELF_LEARNING_FINE_TUNING_SYSTEM.md)
8. [docs/INTEGRATION_SURFACE.md](/Users/Shared/Projects/train/docs/INTEGRATION_SURFACE.md)
