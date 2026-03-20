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
8. [docs/architecture/FEEDBACK_PROMOTION_LOOP.md](docs/architecture/FEEDBACK_PROMOTION_LOOP.md)
9. [AGENT_GUIDE.md](AGENT_GUIDE.md)
10. The current job workspace under `Setup/jobs/<job_name>/`

## Default Working Rule

Do not start from free-form drawing.
Start from the artifact chain:

`draw-job.local.json -> analysis.json -> plan.json -> drawdsl.json -> preview -> review -> lesson`

## First Session Checklist

Use this checklist if you are a newly arrived agent and need to get productive quickly:

1. Read [PROJECT_MANIFEST.json](PROJECT_MANIFEST.json) and [MODE_POLICY.md](MODE_POLICY.md).
2. Identify the active config file and the active job name.
3. Run the job preflight before doing major drawing work:

```powershell
python Setup\run_draw_job.py --config <path-to-config>
```

4. Inspect the job workspace under `Setup/jobs/<job_name>/`.
5. Classify the current blocker before editing:
   - wrong prioritization or missing intent -> `plannerskills`
   - wrong spacing, typography, layout, or routing intent -> `drawskills`
   - Visio operation did not land or could not be controlled -> `visioskills`
   - repeated reusable lesson not yet promoted -> `learningskills`
6. Update artifacts in order instead of jumping straight into ad hoc retries.

If this is your first session in the repository, prefer running the canonical smoke test first:

- guide:
  [docs/human/setup/AGENT_COLD_START_SMOKE_TEST.md](docs/human/setup/AGENT_COLD_START_SMOKE_TEST.md)
- config:
  `Setup/examples/smoke-test-inputpng-1.json`

## Feedback Is Part Of The Job

This repository is still early.
New agents are encouraged to contribute evidence-backed suggestions, not only execute the current job.

Route findings by maturity:

- round-specific observation or friction:
  keep it in `Setup/jobs/<job_name>/reviews/round-*.json`
- cross-job idea that still needs validation:
  write a proposal under `docs/dev/proposals/`
- reusable pattern validated across cases:
  promote it into `agent/skills/learningskills/lessons/`
- proven default behavior:
  update the owning skill, script, schema, or contract

Do not promote a suggestion straight into shared defaults if it only appeared once and has not been localized to the right layer.
For the formal routing rules, see [docs/architecture/FEEDBACK_PROMOTION_LOOP.md](docs/architecture/FEEDBACK_PROMOTION_LOOP.md).

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
