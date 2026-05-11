# Eval Dataset Registry

## Purpose

This document defines the first bounded eval dataset registry in `{train}`.

Use it when replay corpora need to become reusable optimizer inputs instead of ad hoc file lists.

## Current Scope

The registry is intentionally narrow.

It currently supports:

- versioned eval datasets
- saved dataset slices
- explicit scope metadata
- provenance metadata
- deterministic item fingerprints
- resolving proposal bundle inputs from registered datasets or slices

It does not support:

- live runtime data ownership
- remote labeling workflows
- warehouse sync
- heuristic corpus discovery

## Dataset Shape

One eval dataset version is identified by:

- `key`
- `version`

The stable rendered dataset reference is:

- `key@version`

Each dataset stores:

- `name`
- `description`
- `source_kind`
- `scope_kind`
- `scope_value` when scoped
- explicit item list
- provenance metadata
- item count
- deterministic fingerprint

## Dataset Items

Each dataset item stores:

- `item_key`
- absolute local `path`
- optional `labels`

Paths must exist at registration time.

The registry stays local-first by requiring explicit local files rather than abstract source handles.

## Saved Slices

One saved slice is identified by:

- dataset `key`
- dataset `version`
- slice `key`
- slice `version`

The stable rendered slice reference is:

- `dataset_key@dataset_version:slice_key@slice_version`

Each slice stores:

- `name`
- `description`
- `scope_kind`
- `scope_value` when scoped
- explicit `selection_item_keys`
- provenance metadata
- item count
- deterministic fingerprint

Slices are explicit subsets, not query expressions.

That keeps them durable, inspectable, and stable under replay.

## Current API Surface

Datasets:

- `GET /v1/eval-datasets`
- `POST /v1/eval-datasets`
- `GET /v1/eval-datasets/{dataset_key}/versions/{dataset_version}`
- `DELETE /v1/eval-datasets/{dataset_key}/versions/{dataset_version}`

Slices:

- `GET /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/slices`
- `POST /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/slices`
- `GET /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/slices/{slice_key}/versions/{slice_version}`
- `DELETE /v1/eval-datasets/{dataset_key}/versions/{dataset_version}/slices/{slice_key}/versions/{slice_version}`

## Current Execution Reuse

The first execution reuse is in the Trinity proposal services.

Current bounded proposal requests may resolve bundle inputs from:

- raw `bundle_files`
- registered dataset key/version
- registered dataset slice key/version

Current supported proposal surfaces:

- Reply policy proposal service
- Spot review-policy proposal service

## Design Rules

- keep datasets explicit and replayable
- keep saved slices durable and inspectable
- keep scope metadata honest
- keep registry ownership local-first
- do not turn the registry into a second runtime or analytics platform

## Related Documents

- `README.md`
- `docs/SETUP.md`
- `docs/STATUS.md`
- `docs/HANDOVER.md`
- `docs/COMPARISON_HARNESS.md`
