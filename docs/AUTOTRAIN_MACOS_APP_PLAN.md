# Autotrain macOS App Plan

## Purpose

This document defines the plan to deliver `autotrain` as a native macOS application.

It is based on:

- the current `autotrain` browser-first local platform
- the delivery patterns documented in `/Users/Shared/Projects/claude/calendar-agent/DEVELOPMENT.md`
- the `calendar-agent` SwiftPM app structure, bundle scripts, release flow, and update-system implementation

The goal is not just to wrap a browser view. The goal is to build a native operator application that:

- manages local engine processes reliably
- reduces process-watch and restart friction
- supports future automations and background work
- gives us a production-grade macOS delivery path

## What We Should Learn From Calendar Agent

### Lessons To Reuse Directly

1. Native SwiftUI is the correct shell for the macOS operator experience.
2. Delivery must be:
   - error-free
   - warning-free
   - deprecated-free
   - obsolete-free
3. Swift Package Manager should be the default app structure.
4. Build and bundle should be scripted and deterministic.
5. Resources should be managed through dedicated service classes with explicit states.
6. Update delivery should be GitHub-release driven and app-controlled.
7. Critical delivery knowledge must live in repo docs, not in memory.

### Lessons We Should Not Copy Blindly

1. We should not rewrite the `autotrain` engine in Swift.
   Reason: unlike the old Python/PyQt calendar app, `autotrain`'s core value is already in Python and is the right technology for experiment orchestration, benchmarks, adapters, and ML-adjacent work.
2. We should not treat Python bundling as an afterthought.
   Reason: this is the main delivery risk for `autotrain`, and it must be designed explicitly.

## Strategic Product Decision

`autotrain` should become a hybrid native app:

- Native shell: `Swift` + `SwiftUI`
- Core engine: existing `Python` platform
- Control boundary: local `FastAPI` service

This means:

- the macOS app is the operator surface and runtime manager
- the Python service remains the experiment engine
- the native app owns lifecycle, monitoring, recovery, packaging, and update UX

This is the right split because it preserves our strongest existing asset while solving the local operator problems that the browser app does not solve well.

## Target End-State Architecture

### Layer 1: Native macOS App

Responsibilities:

- launch and supervise the local engine
- show run status, logs, providers, agents, project states, recovery state
- expose native controls for:
  - start
  - stop
  - resume
  - open logs
  - install/update resources
- provide background monitoring and user notifications
- manage update installation

Suggested modules:

- `AutotrainApp.swift`
- `AppViewModel.swift`
- `ProcessSupervisorService.swift`
- `EngineHealthService.swift`
- `ProviderResourceService.swift`
- `UpdateService.swift`
- `ArtifactService.swift`
- `AutomationService.swift`

### Layer 2: Embedded Local Engine

Responsibilities:

- existing `FastAPI` app
- existing `SQLite` state
- existing runner, ratchet, providers, projects, and agent adapters

Required app-facing contract:

- stable local API URL and health probe
- structured logs
- explicit startup failure messages
- safe shutdown behavior
- durable state path under app-owned storage

### Layer 3: Local Resource Store

Use macOS app-owned paths, not repo-relative paths, in the shipped product.

Suggested paths:

- app support root:
  - `~/Library/Application Support/Autotrain/`
- engine state:
  - `~/Library/Application Support/Autotrain/state/`
- database:
  - `~/Library/Application Support/Autotrain/state/autotrain.db`
- logs:
  - `~/Library/Application Support/Autotrain/logs/`
- downloaded resources:
  - `~/Library/Application Support/Autotrain/resources/`
- runtime work:
  - `~/Library/Application Support/Autotrain/runtime/`

## Delivery Decision: Browser UI vs Native UI

We should not ship the current `Next.js` app as the primary desktop product.

Recommended approach:

1. keep the browser UI temporarily for development and API inspection
2. build a real native SwiftUI operator UI for the desktop app
3. preserve the API so both UIs can coexist during migration

Reason:

- embedding or depending on the browser UI does not solve process supervision cleanly
- native SwiftUI gives better lifecycle control, notifications, menus, and future automation hooks

## Delivery Decision: Python Runtime Strategy

This is the most important design choice.

### Option A: Full Python Bundling Inside the App

Pros:

- self-contained
- better offline experience

Cons:

- highest packaging complexity
- signing/notarization risk
- large binary
- highest maintenance burden

This should not be MVP.

### Option B: First-Launch Managed Runtime In App Support

Pros:

- keeps Swift app thin
- avoids shipping a giant app bundle
- lets us version and replace the engine/runtime independently
- aligns better with `autotrain`'s fast-moving Python core

Cons:

- first-run setup complexity
- requires explicit runtime bootstrap and integrity checks

This should be MVP.

### Recommended Runtime Plan

For the first native `autotrain` app:

1. ship a native Swift app only
2. on first launch, bootstrap a managed local runtime into App Support:
   - install or verify `uv`
   - create engine venv or managed environment
   - install pinned Python dependencies
   - initialize DB and resource folders
3. run the local FastAPI engine from that managed environment
4. version the runtime independently from the app shell

This is the lowest-risk path that still gives us a real native app.

## Resource Management Plan

This should directly reuse the `calendar-agent` service pattern.

### Pattern

Every external or managed dependency gets:

1. a service class
2. an explicit status enum
3. a status UI component
4. auto-recovery hooks
5. logging and troubleshooting docs

### Resources We Need To Manage

#### 1. Engine Runtime

Service:

- `EngineRuntimeService`

States:

- `unknown`
- `missing`
- `installing`
- `ready`
- `starting`
- `running`
- `stopped`
- `failed`
- `migrating`

Responsibilities:

- verify Python runtime
- verify dependency lock state
- create/update managed environment
- expose engine version

#### 2. Engine Process

Service:

- `ProcessSupervisorService`

States:

- `stopped`
- `starting`
- `running`
- `stalled`
- `restarting`
- `failed`

Responsibilities:

- launch local API
- watch stdout/stderr
- health-check the engine
- restart on bounded failures
- map logs to UI

#### 3. Provider Resources

Service:

- `ProviderResourceService`

Subresources:

- `Mistral API`
- `Ollama`

Responsibilities:

- verify configuration
- verify reachability
- guide install/setup for local provider paths
- show actionable fixes

#### 4. Agent Resources

Service:

- `AgentResourceService`

Subresources:

- `Mistral Vibe`
- future `Cursor`

Responsibilities:

- verify executable presence
- verify contract files
- verify credentials and launch prerequisites

#### 5. Update Resources

Service:

- `UpdateService`

Responsibilities:

- check GitHub releases
- compare versions
- download app update
- later download engine/runtime payload updates

## Process Supervision Plan

This is one of the main reasons to build the native app.

### Native App Must Own

- start local engine on demand
- optionally auto-start at app launch
- show live engine state
- detect stalled or failed local API
- restart the API within bounded rules
- surface operator-visible failure state

### Supervision Contract

The native app should:

1. launch the Python engine with known env vars and known working directory
2. capture stdout/stderr to rotating log files
3. poll `GET /health`
4. poll `GET /v1/operator/status`
5. surface stalled runs and recoverable runs
6. allow safe resume actions from the native UI

### Native Features To Add

- dock badge or menu bar indicator for:
  - engine stopped
  - run active
  - run stalled
  - update available
- macOS notifications for:
  - run completed
  - run failed
  - stalled run detected
  - update ready

## Automation Plan

The native shell gives us a path to future automations the browser app cannot handle cleanly.

### Short-Term

- background health polling
- scheduled update checks
- startup recovery checks
- optional launch-at-login

### Mid-Term

- menu bar helper
- background agent session watcher
- scheduled benchmark or project runs
- native notifications and alerting

### Long-Term

- App Intents / Shortcuts support
- AppleScript or automation hooks
- workflow triggers from calendar/time/system state

## Update System Plan

We should reuse the `calendar-agent` release model with two important modifications.

### What To Reuse

- GitHub Releases as distribution source
- app version check on launch
- periodic update checks
- manual "Check for Updates" action
- download/install/restart flow

### What To Extend For Autotrain

We have two update planes:

1. macOS app shell update
2. Python engine/runtime update

### Recommended Update Design

#### Phase 1

Only update the app shell via GitHub Releases.

The engine runtime stays pinned to the app version and is repaired or refreshed by runtime bootstrap logic.

#### Phase 2

Add engine manifest versioning:

- app version
- engine version
- dependency lock version
- benchmark pack version

Then support:

- app-only update
- engine-only update
- full update

### Update Integrity Requirements

- signed app bundle
- checksum validation for downloaded assets
- version compatibility checks between shell and engine
- rollback-safe install behavior

## Build, Bundle, Sign, Notarize Plan

### Project Structure

Target structure for the native app:

```text
apps/macos/
  Package.swift
  Info.plist
  Sources/
    AutotrainApp.swift
    AppViewModel.swift
    Services/
    Views/
    Models/
  Scripts/
    build.sh
    build-bundle.sh
    notarize.sh
    create-github-release.sh
  Resources/
```

### Build Rules

Follow the `calendar-agent` model:

- `swift build -c release`
- deterministic bundle creation script
- deterministic install location for local testing
- code-sign verification as part of build output

### Packaging Requirements

App bundle should include:

- executable
- `Info.plist`
- app icon
- usage descriptions if needed later
- bundled default config templates

### Signing/Notarization

Delivery sequence:

1. local ad-hoc signing for development
2. Developer ID signing for distribution
3. notarization
4. stapling
5. release ZIP creation

This must be documented before public release.

## Versioning Plan

Use explicit versioning for:

- app shell
- engine runtime
- data/schema

Suggested manifest:

```json
{
  "app_version": "0.1.0",
  "engine_version": "0.1.0",
  "api_contract_version": "1",
  "db_schema_version": "20260430_0002"
}
```

## Migration Plan From Current Browser App

### Phase 0: Freeze Contracts

Before building the app:

- stabilize current API surfaces
- define required operator endpoints
- define app-owned storage layout
- define runtime bootstrap contract

Deliverables:

- native app architecture doc
- runtime bootstrap doc
- update system doc

### Phase 1: Native Shell MVP

Build a SwiftUI app that:

- launches
- shows health
- shows runs
- shows project states
- shows providers
- shows operator status
- can resume recoverable runs

No embedded browser.
No full workflow authoring.
No auto-update yet.

### Phase 2: Runtime Management

Add:

- managed Python runtime bootstrap
- engine start/stop/restart
- log streaming
- failure banners
- first-run installer UI

### Phase 3: Native Operator Controls

Add:

- start run
- stop run
- resume run
- open logs/artifacts
- provider and agent diagnostics

### Phase 4: Update System

Add:

- GitHub release checks
- in-app update prompt
- download/install/restart for shell updates

### Phase 5: Automation Features

Add:

- launch at login
- notifications
- background monitoring
- scheduled checks
- later Shortcuts/App Intents

## Concrete First Build Scope

The first implementation milestone should be:

1. create `apps/macos`
2. create SwiftPM app skeleton
3. create `ProcessSupervisorService`
4. launch the existing local FastAPI engine from the app
5. show:
   - health
   - runs
   - project states
   - providers
   - operator status
6. surface logs in a native "Logs" tab
7. add one native action:
   - `Resume Run`

This is enough to prove the desktop-shell strategy.

## Risks

### Highest Risk

- Python runtime bootstrap and lifecycle management

Mitigation:

- make runtime explicit
- do not hide bootstrap logic
- log every bootstrap step
- use managed app-support paths

### Medium Risk

- keeping shell and engine versions compatible

Mitigation:

- version manifest
- explicit compatibility checks

### Lower Risk

- SwiftUI UI implementation

Mitigation:

- keep the first UI narrow and operator-focused

## Exact Recommendation

Build `autotrain` as a native SwiftUI macOS operator app with a managed local Python engine.

Do not:

- rewrite the engine in Swift
- ship the browser UI as the desktop product
- attempt full embedded Python bundling in MVP

Do:

- use SwiftPM
- use service-based resource management
- use app-owned state paths
- make the native app the process supervisor
- add GitHub-release-based autoupdate after shell MVP

## Execution Order

1. define native app contract docs
2. scaffold `apps/macos`
3. build shell MVP against existing API
4. add runtime bootstrap and supervision
5. replace browser-first desktop usage with native usage
6. add update system
7. add automation features
