# Contributing

## Purpose

This repository is open source and must remain understandable to outside contributors.

Contributions are welcome, but they must follow the project contract and documentation rules in-repo.

Start here before opening implementation work:

- [README.md](./README.md)
- [docs/OPERATING_MODEL.md](./docs/OPERATING_MODEL.md)
- [docs/TECH_STACK.md](./docs/TECH_STACK.md)
- [docs/OPEN_SOURCE.md](./docs/OPEN_SOURCE.md)
- [docs/REPOSITORY_CONTRACT.md](./docs/REPOSITORY_CONTRACT.md)

## Contribution Rules

1. Work from an issue.
2. Keep implementation aligned with the documented repository contract.
3. Update docs in the same change when architecture, operations, or interfaces change.
4. Do not introduce hidden setup or recovery knowledge.
5. Keep engine logic, project logic, agent adapters, and provider adapters separate.

## Before You Start

Confirm:

- the issue has clear acceptance checks
- the issue scope is current
- the change belongs to the current roadmap phase
- the relevant docs exist or are updated in the same change

If the issue is vague, fix the issue first.

## Branch Naming

Use:

- `issue-<number>-<slug>`

Examples:

- `issue-4-engine-runner`
- `issue-9-provider-adapters`

## Commit Naming

Use:

- `<area>: <change>`

Examples:

- `docs: define repository contract`
- `engine: add run result schema`
- `api: add health endpoint`

## Pull Request Expectations

Each PR should:

- reference the issue
- state the scope clearly
- state any docs updated
- state how the change was verified
- state any operational impact

Use this title shape:

- `[ISSUE-<number>] <title>`

## Required Co-Changes

Update docs in the same PR when you change:

- architecture
- stack choices
- environment model
- repository structure
- adapter boundaries
- deployment behavior
- setup or recovery procedures

## Review Standard

Reviews should check:

- correctness
- boundary discipline
- documentation completeness
- operational clarity
- adherence to the repository contract

## Definition Of Done

A contribution is done only when all are true:

- code is implemented
- acceptance checks pass
- docs are updated if required
- operational impact is documented if required
- the issue can be updated truthfully

## License

By contributing to this repository, you agree that your contributions are submitted under the terms of the `Apache-2.0` license used by this project.
