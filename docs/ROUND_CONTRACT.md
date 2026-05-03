# Round Contract

## Purpose

This document defines the round-based research contract for serious `{train}` work.

Use it when a project is doing more than a one-off proof or smoke benchmark.

The goal is to make learning explicit, repeatable, and skeptically reviewable.

## Why This Exists

`{train}` already has the bounded optimization loop:

1. define a project contract
2. mutate a controlled artifact
3. run one bounded experiment
4. produce one automatic score
5. compare against prior state
6. keep or reject the change

That loop is necessary but not sufficient for disciplined learning.

Without a round contract:

- project work drifts into ad hoc experimentation
- scores move without a clear hypothesis
- future contributors cannot tell what was actually being tested
- proof scripts become isolated artifacts instead of a reusable learning method

The round contract solves that problem.

## What A Round Is

A round is one explicit bounded learning cycle around a project component.

A round is not:

- an open-ended research phase
- a product roadmap bucket
- a chat thread
- a collection of unrelated experiments

A round is:

- one hypothesis
- one declared baseline
- one candidate change set
- one bounded budget
- one controlled comparison
- one main decision
- one next-step recommendation

## When To Use It

Use the round contract when:

- the project matters enough to justify explicit reasoning
- the result may influence future optimization direction
- the work is intended to be replayed or handed off
- the project is optimizing a runtime component from another system such as `{trinity}`
- the project is moving from proof-of-concept toward real learning discipline

You do not need the full contract for every tiny fixture or trivial smoke test.

## Round Scope

Each round must stay bounded.

A valid round should have:

- one project key
- one primary question
- one controlled mutable artifact set
- one declared score path
- one bounded execution budget

If the round needs multiple unrelated questions answered at once, split it.

## Required Round Artifacts

Each serious round should define or produce the following artifacts.

### 1. Hypothesis

State:

- what component is under optimization
- what should improve
- why that improvement is expected
- what metric should move
- what failure would mean

This may later live in a dedicated hypothesis artifact, but the round contract requires the concept now.

### 2. Baseline

State:

- what the incumbent behavior is
- what artifact/version/commit is the baseline
- what score or output currently represents the baseline

The baseline must be concrete enough to compare against later.

### 3. Candidate

State:

- what exact change is being tested in this round
- which mutable artifacts are allowed to change
- what is intentionally out of scope

The candidate must remain bounded by the project contract.

### 4. Budget

State:

- runtime budget
- any dataset/sample restrictions
- execution limits relevant to honest comparison

Budget must be explicit, not inferred.

### 5. Comparison

State:

- what baseline, candidate, and incumbent are being compared
- whether the inputs are fixed
- whether the evaluation path is identical
- what direct deltas matter

The comparison harness may be implemented later, but the round contract requires the comparison semantics now.

### 6. Main Decision

State:

- accepted
- rejected
- inconclusive

This is the round-level interpretation.

It does not replace ratchet semantics. It explains the learning outcome.

### 7. Next Step

State:

- what should happen next if the round succeeded
- what should happen next if the result was weak or inconclusive
- whether to continue, narrow, escalate, or stop

The round must not end without a forward recommendation.

## Optional But Recommended Round Artifacts

### Minority Report

Use when:

- the metric improved but confidence is weak
- the benchmark may be overfit
- the result may not generalize
- the explanation for the improvement is unclear
- the system is prone to optimistic interpretation

The minority report should capture:

- the strongest skeptical interpretation
- hidden confounds
- overfitting risks
- weak assumptions
- what to test next to disprove ourselves

### Round Report

Use when:

- a project is expected to run multiple meaningful rounds
- handoff quality matters
- the result should be easy to review later

The report can be human-readable, machine-readable, or both.

## Standard Round Lifecycle

One serious round should follow this order:

1. define the question
2. state the hypothesis
3. pin the baseline
4. declare the candidate and mutable scope
5. declare the budget
6. run the bounded experiment
7. compare baseline, candidate, and incumbent
8. record the main decision
9. record the minority report when needed
10. define the next step

## Mapping To Existing `{train}` Mechanics

The round contract does not replace the existing engine.

It sits on top of it.

### Project Contract

The project contract still owns:

- mutable artifacts
- setup artifacts
- dependency artifacts
- metric definition
- run entrypoint
- budget bounds

The round contract must never weaken these.

### Run Lifecycle

The run lifecycle still owns:

- `pending`
- `running`
- `succeeded` or `failed`
- ratchet evaluation

A round may use one or more runs, but a serious round should still present one coherent learning story.

### Ratchet

The ratchet still owns:

- keep or reject decisions at the artifact level
- best-so-far tracking
- commit or restore behavior

The round contract must not replace ratchet mathematics with subjective judgment.

Instead:

- ratchet answers whether the candidate is mechanically better under the score path
- the round answers what we learned and what to do next

## Round Decision Rules

Keep these distinctions explicit:

### Accepted

Use when:

- the candidate improved under the automatic score path
- the result is strong enough to advance the project

### Rejected

Use when:

- the candidate regressed
- the candidate violated a relevant constraint
- the change was not worth keeping

### Inconclusive

Use when:

- the metric moved but interpretation is weak
- the score is too noisy
- the benchmark is not strong enough yet
- the candidate did not meaningfully answer the round’s question

Do not hide inconclusive rounds by pretending they were wins.

## Comparison Rules

Every serious round should aim for:

- same input set
- same budget
- same score path
- direct delta table

If one of these changes, the round must say so explicitly.

This is especially important for:

- `{reply}` work with evolving private data
- future OpenMythos-like external research-system projects
- comparisons across multiple bounded runtime components

## Boundary Rules

The round contract must not break the platform boundaries.

### Do Not Do This

- do not let a round mutate artifacts outside the project contract
- do not let a round silently widen benchmark inputs
- do not let runtime concerns from `{trinity}` leak into `{train}` core
- do not let research narration replace automatic scoring
- do not let skeptical commentary block clear ratchet outcomes without evidence

### Do This Instead

- keep the project bounded
- keep the score automatic
- keep the comparison explicit
- keep the decision honest
- keep the next step concrete

## Recommended Minimal Round Template

Use this shape:

```text
Round ID:
Project:
Component:

Hypothesis:
Baseline:
Candidate:
Budget:
Comparison Method:

Run IDs:
Metric Result:
Ratchet Result:

Main Decision:
Minority Report:
Next Step:
```

## How This Applies To Project Types

### Reference Benchmarks

Use rounds to:

- prove score movement honestly
- compare benchmark changes consistently
- keep project history easy to review

### `{trinity}`-Style Runtime Components

Use rounds to:

- optimize one bounded runtime component
- tie the component to a score path
- explain what the runtime change is supposed to improve

### OpenMythos-Like External Research Systems

Use rounds to:

- isolate one hypothesis
- prevent research repos from becoming architectural exceptions
- keep benchmark framing strong without importing monolithic repo shapes

## Success Criteria

This contract is working when:

- future agents know how to structure one serious learning cycle
- projects stop shipping vague proof stories
- score movement is easier to interpret
- future rounds have better continuity
- the platform becomes stronger at learning, not only at ratcheting

## Final Rule

A round is only complete when it leaves behind:

- a clear question
- a bounded comparison
- an explicit decision
- a concrete next step

If one of those is missing, the round is not yet rigorous enough.
