# Contributing to DrawForge

DrawForge is trying to become more than a one-off diagram conversion demo.
The long-term goal is to accumulate reusable agent-facing capabilities around planning, drawing, execution, review, and learning.

This means contributions are not only code patches.
Useful contributions also include:

- bug reports with reproducible evidence
- operator or agent friction reports
- benchmark jobs
- structural proposals
- validated reusable lessons
- skill, schema, and bridge improvements

The key question is:

"What should be added, and where, so the next person or agent does not have to rediscover it?"

## Contribution philosophy

Please help the repository grow in a way that preserves signal:

- keep raw evidence close to the job that produced it
- promote only reusable ideas into shared knowledge
- change shared defaults only when the problem is truly structural
- avoid mixing round memory, design hypotheses, and validated lessons into one bucket

The intended promotion path is:

`review -> proposal -> lesson -> shared default behavior`

## GitHub intake routes

If you are contributing through GitHub, start with the closest matching intake path:

- Bug report
  - use when something is broken or behaves incorrectly
- Structural proposal
  - use when you see a likely system-level improvement that still needs validation
- Lesson candidate
  - use when you discovered reusable experience that future agents should inherit
- Pull request
  - use when the right shared repo change is already clear enough to implement

These templates live under `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`.

## Where different contributions belong

### 1. Round-specific findings

Use this when the finding is mostly about one job or one drawing round.

Store or reference:

- `Setup/jobs/<job_name>/reviews/round-*.json`
- preview PNGs under `OutputPreview/`
- execution artifacts in the active workspace

Examples:

- a connector crossed the wrong region in one benchmark
- a title overlapped a container in one round
- a particular layout retry made things worse

This is evidence, not yet shared repo knowledge.

### 2. Structural ideas that still need validation

Use this when the issue looks likely to repeat across jobs, but the right fix is not proven yet.

Write a proposal under:

- `docs/dev/proposals/`

Use this for:

- missing controls in `visioskills`
- repeated layout friction in `drawskills`
- review blind spots
- unclear layer boundaries
- onboarding problems for new agents

Examples:

- "reference links need routing guardrails"
- "new agents need a canonical cold-start smoke test"

Proposal means:

- the idea matters
- the owner layer is becoming clear
- more validation is still needed

### 3. Validated reusable experience

Use this when the pattern is already clear enough that future agents should reuse it directly.

Write a lesson under:

- `agent/skills/learningskills/lessons/`

Good lessons explain:

- the root cause
- how to detect it earlier
- which layer should absorb the rule
- what future agents should do differently

Examples:

- text size, box size, and gap must be adjusted together
- vertical text needs text-block handling, not only angle changes

Lesson means:

- the repo has moved beyond a hypothesis
- the knowledge is useful outside one single job

### 4. Shared default behavior

Use this when the repository should stop rediscovering the same fix.

Change the owning shared layer:

- `agent/skills/plannerskills/`
- `agent/skills/drawskills/`
- `agent/skills/visioskills/`
- `agent/skills/learningskills/`
- `Setup/`
- `docs/architecture/`

Examples:

- add a missing bridge operation
- strengthen DrawDSL review checks
- update a schema to capture an important concept
- improve cold-start documentation

## Quick routing guide

Use this shortcut:

- If it happened in one round and you mainly want to preserve evidence:
  keep it in `reviews/`
- If it looks systemic but you are not ready to hardcode the fix:
  write a `proposal`
- If it is already reusable advice:
  write a `lesson`
- If you know the fix belongs in shared behavior now:
  patch the repo directly

You do not need to write a proposal first for every hard bug.
If the fix is obvious and clearly belongs in shared code or skills, fixing it directly is fine.

## What to include in a contribution

Whether you open an issue, write a proposal, add a lesson, or send a PR, try to include:

- the job name or benchmark name
- the input figure context
- what you expected
- what actually happened
- which artifact shows the problem
- the suspected owner layer, if known
- whether this feels round-specific or reusable

Useful evidence includes:

- preview PNG paths
- review snippets
- execution warnings
- benchmark references
- small redacted diagrams if the original cannot be shared

## For users and external agents

If you are using DrawForge outside the main maintained benchmark set, you do not need to upstream every local review.

A good public contribution usually looks like one of these:

1. A reproducible issue with evidence
2. A proposal document that captures a likely structural gap
3. A lesson that has already been validated
4. A PR that updates shared docs, skills, schemas, or code

In short:

- keep private local job history local unless it is useful to others
- upstream the reusable part

## For maintainers and contributors changing shared behavior

Before promoting a finding into shared behavior, ask:

1. Is this only about one figure?
2. Would another job likely hit the same problem?
3. Which layer should own the fix?
4. Are we promoting a hypothesis too early?

If the answer is still unclear, prefer a proposal over a direct default.

## Files that usually should not be committed casually

Avoid committing runtime-only or machine-specific material unless the task explicitly needs it:

- `.runtime/`
- local tokens or secrets
- machine-specific logs
- one-off temporary exports

Tracked benchmark workspaces under `Setup/jobs/` should be updated carefully and intentionally.

## Good first contributions

If you are new to the project, strong first contributions include:

- improving onboarding docs
- improving smoke tests
- filing a well-scoped proposal
- promoting a repeated review finding into a lesson
- fixing a clearly localized bridge or layout bug

## Related documents

- [README.md](README.md)
- [AGENT_START_HERE.md](AGENT_START_HERE.md)
- [MODE_POLICY.md](MODE_POLICY.md)
- [docs/architecture/FEEDBACK_PROMOTION_LOOP.md](docs/architecture/FEEDBACK_PROMOTION_LOOP.md)
- [docs/dev/proposals/README.md](docs/dev/proposals/README.md)
