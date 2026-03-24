# Feedback Promotion Loop

This document explains how DrawForge should treat feedback from agents and humans.

The repository is still early.
That means suggestions, friction reports, and "this should be easier" observations are valuable.
But they should not all go straight into shared defaults.

## The promotion ladder

Route feedback by maturity:

1. Round memory
   - file: `Setup/jobs/<job_name>/reviews/round-*.json`
   - use for job-specific evidence, friction, missed checks, and next actions
2. Proposal
   - file: `docs/dev/proposals/*.md`
   - use for structural ideas that look promising but still need validation
3. Lesson
   - file: `agent/skills/learningskills/lessons/*.md`
   - use for reusable patterns validated across cases
4. Default behavior
   - target: skills, scripts, schemas, bridge code, or contracts
   - use only when the project wants the behavior by default

## What counts as valuable feedback

Good feedback is not only "the picture looks wrong."
It can also be:

- an operation the agent needed but could not express
- a review blind spot that let a bug survive
- repeated friction in layout planning or job setup
- confusion about which layer owns a failure
- a missing abstraction that forced brittle one-off work

## How to decide where a finding belongs

Ask four questions:

1. Is this only about the current round?
2. Would another job likely hit the same problem?
3. Do we know the owning layer yet?
4. Is the fix proven enough to become shared behavior?

If the answer to 1 is yes, keep it in the round review.
If the answer to 2 is yes but 4 is no, write a proposal.
If the answer to 2 and 4 is yes, promote it into a lesson or a direct repo update.

## Example promotion path

Example:

- round review:
  "The agent could not keep long narrow labels readable without manual text rotation and box reflow."
- proposal:
  "DrawDSL should support an explicit narrow-label readability policy with vertical-text fallback."
- lesson:
  "Vertical text needs text-block synthesis and spacing reflow, not only angle changes."
- default behavior:
  `drawskills` and `visioskills` are updated so the fallback is no longer rediscovered from scratch

## Promotion discipline

Do not do these:

- do not dump raw execution logs into lessons
- do not promote a one-time opinion directly into shared defaults
- do not leave a repeated structural pain point only inside one job review
- do not force every good idea into code immediately

The point of this loop is to preserve signal while keeping the repository teachable for the next agent.
