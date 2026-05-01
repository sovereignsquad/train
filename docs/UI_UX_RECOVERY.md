# UI/UX Recovery

## Purpose

This document records what went wrong in the first native macOS shell UI pass and what was changed to correct it.

It exists because this failure mode should not repeat.

## What Went Wrong

The initial shell UI violated several basic desktop-product expectations:

- primary actions were placed directly inside the content area instead of the native toolbar
- project editing relied on oversized freeform text fields instead of native selection controls
- artifact fields were presented as raw multiline text with weak affordance and no clear structure
- the project editor layout did not adapt well to smaller window widths
- the app behavior was not always re-validated from the rebuilt `.app` bundle after source edits
- interaction quality depended too much on implementation convenience and not enough on operator usability

That combination made the app feel like a stretched internal prototype instead of a usable native tool.

## Recovery Changes

The corrective changes in `apps/macos` were:

- moved `Refresh`, `Check Updates`, `Start Engine`, and `Stop Engine` into the native window toolbar
- removed the floating in-content button cluster from the project page
- lowered overly rigid minimum window sizing so the shell can contract more naturally
- rebuilt the project editor into explicit sections:
  - identity
  - execution
  - budget
  - artifacts
- replaced raw artifact text blobs with:
  - native file browse controls for single-path fields
  - editable list controls for multi-path artifact groups
  - native pickers for metric direction, runner key, and template selection
- replaced the long Projects card wall with a native list-detail selection layout
- enabled text selection on key read-only values and project metadata surfaces
- made the shell warning-free again by fixing Swift actor-isolation issues around `NSOpenPanel`

## Responsibility Standard

Native UI work in this repository must follow these rules:

- use native control placement before inventing custom action layouts
- use pickers, lists, and file selectors when the user is choosing from structured data
- do not expose multiline raw path entry as the primary artifact-management workflow
- verify usability from the rebuilt local `.app`, not only from source inspection
- do not merge a UI pass that is visibly ambiguous about what elements do

If a UI change fails those checks, it is not ready.

## Files Changed In Recovery

Primary files:

- `apps/macos/Sources/TrainApp.swift`
- `apps/macos/Sources/Views/ContentView.swift`
- `apps/macos/Sources/Views/ProjectManagementView.swift`

Supporting validation:

- `apps/macos/Scripts/build-bundle.sh`
- `docs/STATUS.md`
- `docs/HANDOVER.md`

## Verification

Recovery was verified with:

- `swift build -c release`
- `bash apps/macos/Scripts/build-bundle.sh`
- `uv run ruff check .`
- `uv run pytest`

The updated local bundle is:

- `apps/macos/dist/Train.app`
