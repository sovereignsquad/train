# Coding Standards

## Purpose

This document defines the minimum coding standards for `{train}`.

## Native App Rules

- Treat `{train}` as a native macOS product, not a website, when touching shipped operator surfaces.
- The primary `{train}` macOS workspace must be pure SwiftUI/AppKit.
- Do not move core operator flows back into HTML/CSS/JavaScript or browser-style shells.
- Local services, APIs, and background processes are acceptable, but they remain internal infrastructure behind the native app.
- Keep shipped visual assets local and reliably available offline.
- Use explicit rendering contracts instead of heuristic parsing of markup, icons, and asset values.
- Use one local icon system and one shared icon size contract across app-controlled surfaces.
- Keep icon buttons consistent across shell chrome, status surfaces, project controls, settings, and dialogs.
- Do not use emoji or ad hoc glyphs as shipped product iconography.
- Verify readability in day mode, night mode, and system-follow mode for UI changes.
- Verify user-facing changes against the installed native app, not only source previews.

## Platform Rules

- Keep platform layers explicit and separate.
- Prefer deterministic local behavior over implicit framework magic.
- Keep operator state, project state, and engine state clearly separated.
- Keep `{train}` as an offline optimizer: do not blur exported artifact consumption with live runtime ownership.
- Add new learner lanes only against explicit exported contracts; do not infer hidden runtime state or mutate live runtime behavior directly.
- Keep proposal artifacts, eval reports, and comparison outputs explicit, versioned, and replayable.

## Code Comments

- Use comments sparingly and only when they clarify a non-obvious contract, invariant, or boundary.
- Keep comments synchronized with implemented behavior; stale explanatory comments are a bug.
- When a learner is intentionally narrow, say exactly what is and is not learned.
- Do not write comments that imply broader product/runtime ownership than the code actually has.

## Open-Source Documentation

- Keep public docs aligned with the shipped repo state, not an older lane or a future roadmap.
- If `{train}` supports a bounded adapter slice, the README and setup docs must say so explicitly.
- If scope support changes, update the README, setup docs, architecture docs, and handover/status docs in the same tranche.
- Do not describe a capability as generic or multi-adapter when it is still intentionally narrow.

## Documentation

- Update docs whenever architecture, workflow ownership, or native app behavior changes.
- For meaningful repo changes, update `README.md`, `docs/STATUS.md`, and `docs/HANDOVER.md` together unless there is a clear reason not to.
