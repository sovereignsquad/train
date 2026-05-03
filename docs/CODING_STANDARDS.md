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

## Documentation

- Update docs whenever architecture, workflow ownership, or native app behavior changes.
