# Handover

## Purpose

This document exists so work can be resumed cleanly by:

- the same developer later
- another developer
- another coding agent

It is the short-term transfer document.

## How To Use

When ending a meaningful work session, update:

- what changed
- what was verified
- what remains next
- what must be watched carefully

Keep this document concise and current.

## Current Handover

### What Changed Last

Last completed increment:

- first ratchet decision layer increment for `ISSUE-5`

Implemented:

- project state ledger
- best-score comparison model
- ratchet decision fields on run records
- `ratchet` endpoint
- git head / dirty-state capture at ratchet time

### What Was Verified

Verified:

- ratchet decisions work across multiple runs
- first successful run becomes the baseline
- better run replaces best-so-far
- worse run is rejected while preserving project best state
- project-state endpoint reflects best run and last run correctly

### What Needs To Happen Next

Next expected work:

1. verify ratchet decisions across multiple runs
2. decide whether to automate git keep/revert now or after the repo is cleaner
3. replace the placeholder mythology execution path with real benchmark behavior later
4. prepare the handoff for the next lane

### Watch Carefully

- keep engine code generic
- do not hardcode mythology-specific logic into `core/`
- keep agent adapter work out of runner core for now
- avoid premature migrations framework until schema stabilizes a bit more
- keep the placeholder benchmark clearly marked as placeholder

### If You Only Have 30 Minutes

Do this:

- verify the ratchet API against multiple runs
- inspect project-state updates
- update `docs/STATUS.md`

### If You Have A Full Session

Do this:

- verify and harden the ratchet lane
- decide the git keep/revert boundary for the next increment
- keep the mythology benchmark placeholder clearly temporary
- prepare the handoff for the next lane
