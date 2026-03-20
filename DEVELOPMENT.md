# Development

This file is the human entry point for working on the system itself rather than only running a single job.

## Use This When

- you are changing schemas, skills, bridge behavior, or execution scripts
- you are reorganizing repository structure or documentation
- you are improving generic layout or review rules
- you are deciding what should become a long-term asset

## Recommended Read Order

1. [README.md](README.md)
2. [MODE_POLICY.md](MODE_POLICY.md)
3. [AGENT_START_HERE.md](AGENT_START_HERE.md)
4. [AGENT_GUIDE.md](AGENT_GUIDE.md)
5. [docs/README.md](docs/README.md)
6. [docs/architecture/README.md](docs/architecture/README.md)
7. [docs/dev/README.md](docs/dev/README.md)

## Development Areas

- `plannerskills/`
  - figure understanding and task orchestration
- `drawskills/`
  - layout rules, DrawDSL generation, figure-building logic
- `visioskills/`
  - bridge, operator guidance, execution semantics
- `learningskills/`
  - reusable lessons and promotion rules
- `Setup/`
  - job bootstrap, schemas, execution scripts

## Development Mode

When a job is running in `development` mode, repo-level changes are allowed if the issue is structural rather than job-specific.

Examples:

- adding a missing Visio operation
- correcting a generic connector default
- improving a reusable review rule
- clarifying documentation or contracts

## Verification Expectations

Before closing development work, verify as much as the change allows:

- schema or JSON validity for config and artifact changes
- script syntax for Python changes
- exported preview improvements for drawing changes
- updated links for doc moves or entrypoint changes

## Useful Docs

- Doc index: [docs/README.md](docs/README.md)
- Architecture docs: [docs/architecture/README.md](docs/architecture/README.md)
- Human-facing operational docs: [docs/human/README.md](docs/human/README.md)
- Development docs: [docs/dev/README.md](docs/dev/README.md)
