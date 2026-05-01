# Open Source Policy

## License Choice

`{train}` uses the `Apache-2.0` license.

## Why Apache-2.0

We want the project to be:

- easy to adopt
- easy to contribute to
- safe to use in commercial and internal environments
- compatible with a broad ecosystem of adapters, integrations, and benchmarks

`Apache-2.0` is the best default for this project because it is permissive and includes an explicit patent grant.

That matters for a platform that may eventually include:

- agent adapters
- provider adapters
- orchestration logic
- infrastructure integrations
- third-party contributions

## Project Policy

All repository content should assume:

- open development
- public documentation
- reusable architecture
- contribution-friendly interfaces

## Documentation Rule

Anything important to contributors or downstream adopters must be documented in-repo.

That includes:

- stack decisions
- operating model
- repository contract
- environment model
- deployment model
- contribution expectations

## Contribution Assumption

Unless explicitly stated otherwise, contributions submitted to the repository are intended to be accepted under `Apache-2.0`.

## Practical Implications

When writing code and docs:

- keep interfaces readable and reusable
- avoid vendor lock-in in platform contracts
- separate core platform logic from project-specific benchmarks
- keep third-party integration boundaries explicit

## Future Supporting Files

As the project grows, we should add:

- `CONTRIBUTING.md`
- `NOTICE` if required by future attributions
- `docs/REPOSITORY_CONTRACT.md`
- `docs/ARCHITECTURE.md`

## Reference

- OSI Apache 2.0 page: [opensource.org/license/apache-2.0](https://opensource.org/license/apache-2.0)
