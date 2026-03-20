# Mode Policy

This document defines how agents and humans should treat repository mutability in different run modes.

## Core Rule

Start with the narrowest write scope that can solve the task.
Only expand outward when the blocker is clearly structural.

## Run Modes

### `operation`

Purpose:

- run or review a drawing job
- keep repo-wide behavior stable

Default writable areas:

- `InputReference/`
- `Setup/draw-job.local.json`
- `Setup/jobs/`
- `OutputPreview/`
- `OutputEditable/`

Frozen by default:

- `agent/skills/plannerskills/`
- `agent/skills/drawskills/`
- `agent/skills/visioskills/`
- `agent/skills/learningskills/`
- `docs/`
- shared scripts and schemas under `Setup/`

Use this mode when the task is mainly about completing the current job.
Cross-job suggestions should usually stay inside the current round review unless a human explicitly asks for repo-level follow-up.

### `development`

Purpose:

- improve the system itself
- fix structural blockers
- update reusable assets

Writable areas:

- the active job workspace
- shared docs
- shared skills
- bridge code
- execution scripts
- schemas and contracts

Use this mode when the problem cannot be solved cleanly inside one job workspace.

In this mode, evidence-backed proposals under `docs/dev/proposals/` are allowed and encouraged.

## Recommended Write Scopes

These are policy concepts even if a given config file does not yet store them explicitly.

### `job_only`

Change only:

- job-local artifacts
- previews
- final outputs

### `repo_and_job`

Change:

- job-local artifacts
- reusable repo assets needed to fix the blocker

## Promotion Rule

When a finding generalizes:

- keep it in `reviews/` if it is still round-specific
- keep it in `docs/dev/proposals/` if it looks structural but still needs validation
- promote it to `agent/skills/learningskills/` if it is reusable
- update `agent/skills/plannerskills/`, `agent/skills/drawskills/`, `agent/skills/visioskills/`, `Setup/`, or docs only if it should become a default repo behavior

## Feedback Routing Shortcut

Use this simple routing rule:

1. Raw observation from this round -> `reviews/`
2. Structural idea not proven enough yet -> `docs/dev/proposals/`
3. Proven reusable pattern -> `learningskills/`
4. Mature default behavior -> repo code, skills, schema, or contracts

This keeps the repo open to agent suggestions without turning shared skills into an unfiltered idea dump.

## Decision Shortcut

Ask:

1. Is this problem only about the current figure?
2. Would another job likely hit the same problem?
3. Is the missing behavior a layout rule, an execution ability, a planning rule, or a documentation gap?

If the answer only affects the current figure, stay local.
If the answer clearly affects future jobs, a development-mode change is appropriate.
