# Agent Start Here

This is the cold-start entry point for any new agent entering the repository.

Start here before reading the detailed workflow guide.

## Minimum Capabilities

An agent working effectively in this repository should ideally be able to:

- read and write local files
- run shell commands
- inspect exported preview images
- call the local Visio bridge over HTTP
- follow JSON and Markdown contracts

Without those capabilities, the repository can still be read, but not fully operated.

## Read Order

1. [PROJECT_MANIFEST.json](PROJECT_MANIFEST.json)
2. [MODE_POLICY.md](MODE_POLICY.md)
3. [agent/README.md](agent/README.md)
4. [agent/skills/README.md](agent/skills/README.md)
5. [Setup/README.md](Setup/README.md)
6. [docs/architecture/LAYER_CONTRACTS.md](docs/architecture/LAYER_CONTRACTS.md)
7. [docs/architecture/ARTIFACT_CONTRACTS.md](docs/architecture/ARTIFACT_CONTRACTS.md)
8. [AGENT_GUIDE.md](AGENT_GUIDE.md)
9. The current job workspace under `Setup/jobs/<job_name>/`

## Default Working Rule

Do not start from free-form drawing.
Start from the artifact chain:

`draw-job.local.json -> analysis.json -> plan.json -> drawdsl.json -> preview -> review -> lesson`

## Mode Awareness

Before making changes, check the current mode:

- In `operation` mode, stay mostly inside the active job workspace and outputs.
- In `development` mode, structural repo changes are allowed when the blocker is systemic.

The detailed write rules are defined in [MODE_POLICY.md](MODE_POLICY.md).

## When To Escalate From Job Work To Repo Work

Move from job-local fixes to repo-level fixes only when the problem is structural, for example:

- the bridge lacks a needed operation
- a default layout rule is clearly wrong across jobs
- the schema or contracts are missing an important concept
- the review mechanism is repeatedly missing the same kind of failure

## Next Document

After this file, continue with [AGENT_GUIDE.md](AGENT_GUIDE.md) for the detailed operating workflow.
