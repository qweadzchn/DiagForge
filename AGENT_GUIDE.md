# AGENT_GUIDE

This is the detailed operating guide for agents already entering the repository.

If you are starting cold, read [AGENT_START_HERE.md](AGENT_START_HERE.md) first.

The goal is not "call a few Visio APIs".
The goal is "understand what to draw, why it should look that way, which controls are needed, how to verify the result, and how to improve the next round".

## Core model

- `Setup` decides which job is running, where artifacts go, how many rounds are allowed, and what gets saved.
- `plannerskills` decides what the input figure is, which regions matter, what should be drawn first, and which capabilities are needed.
- `drawskills` turns that plan into layout, typography, spacing, and DrawDSL.
- `visioskills` executes explicit Visio operations reliably.
- `learningskills` turns repeated failures and fixes into reusable lessons.

These reusable skill layers now live under `agent/skills/`.

Do not collapse these layers into one giant prompt.

## Read order for a new job

1. `Setup/draw-job.local.json`
2. `docs/architecture/LAYER_CONTRACTS.md`
3. `docs/architecture/ARTIFACT_CONTRACTS.md`
4. The relevant `SKILL.md`
5. The current job artifacts in `Setup/jobs/<job_name>/`

## Standard workflow

1. Preflight the bridge and token.
2. Produce or update `analysis.json`.
3. Produce or update `plan.json`.
4. Produce or update `drawdsl.json`.
5. Execute in Visio.
6. Export preview PNG.
7. Write `round-review.json`, including friction and structural gaps when present.
8. If the idea is structural but not fully proven, write a proposal under `docs/dev/proposals/`.
9. Promote reusable validated findings into `learningskills`.

## First-time agent stance

If you are the first agent touching a job, do not assume the repo is wrong and do not assume it is complete.
Work from evidence:

- preflight first
- inspect the current workspace
- localize the blocker to the correct layer
- leave artifacts that let the next agent continue without guesswork

The goal is to make the repository easier for the next agent, not only to finish one run.

## The closed-loop rule

Every meaningful drawing task must answer four questions explicitly:

1. What are we trying to draw?
2. Which operations and controls are needed to draw it well?
3. How will we know it worked?
4. If it failed, which layer owns the fix?

This rule lives primarily in `plan.json`, not only in the operator's head.

## Plan-to-operation loop

`plan.json` should not stop at strategy like "make text readable".
It must also contain closed-loop intent bundles:

- the drawing intent
- the target region
- the drawskills responsibilities
- the visioskills operation bundle
- the verification signals
- the failure routing rules

Example:

- Intent: keep narrow modules readable
- Drawskills: choose line breaks, font size band, minimum width, gap policy
- Visioskills: `shape/add`, `shape/set_text_style`, `shape/set_text_block`, `shape/describe`
- Verification: no overflow, font landed, box size matches text, neighbors do not collide
- Failure routing:
  - if font or text block did not land -> `visioskills`
  - if font landed but modules still collide -> `drawskills`
  - if the wrong region was prioritized -> `plannerskills`

## Improvement gate

"Next round must be better" is not a slogan here.
It means:

1. Every round exports a preview.
2. Every round review names concrete problems.
3. The next round writes those problems back into `plan.json`.
4. The next round preserves what already improved.
5. If a rerun does not solve a prior issue or add useful new information, it is not progress.

## Feedback and proposal loop

In this repository, agent feedback is a feature, especially in `development` mode.
But feedback should be routed cleanly:

- raw round memory:
  `Setup/jobs/<job_name>/reviews/round-*.json`
- still-hypothetical cross-job improvement:
  `docs/dev/proposals/*.md`
- validated reusable rule:
  `agent/skills/learningskills/lessons/*.md`
- default repo behavior:
  the owning skill, bridge code, schema, script, or contract

Useful feedback includes:

- controls the agent expected but could not find
- repeated operator friction
- review blind spots
- layer boundary confusion
- missing abstractions that made a good plan hard to execute

Do not turn every opinion into a lesson.
Do not leave structural ideas only as one-off review notes if they are likely to matter again.

## When to change the repo

In `development` mode, the agent may change:

- schemas
- docs
- drawskills references
- visio bridge code
- execution scripts

This is correct when the blocker is structural rather than job-specific.

In `operation` mode, the agent should mostly stay inside the job workspace and output artifacts.

## What good execution looks like

- Clear layer boundaries
- Traceable artifacts
- Explicit plan-to-operation mapping
- PNG previews for review
- Verified execution when possible
- Reusable lessons when a fix generalizes

## What not to do

- Do not blame layout when the bridge has not been verified.
- Do not stuff one-off patches directly into generic skills without review.
- Do not let `visioskills` silently make planning decisions.
- Do not let `drawskills` become a long-term lesson dump.
- Do not rerun unchanged work and call it improvement.

## Key files

- `docs/architecture/LAYER_CONTRACTS.md`
- `docs/architecture/ARTIFACT_CONTRACTS.md`
- `docs/architecture/PLAN_TO_OPERATION_LOOP.md`
- `docs/architecture/FEEDBACK_PROMOTION_LOOP.md`
- `docs/human/PREVIEW_REVIEW_CHECKLIST.md`
- `Setup/analysis.schema.json`
- `Setup/plan.schema.json`
- `Setup/round-review.schema.json`
- `agent/skills/visioskills/OPERATIONS.md`
