# ARTIFACT_CONTRACTS

This document defines what each standard artifact means.

If `LAYER_CONTRACTS.md` answers "who decides what", this file answers "what should each file express".

## Standard artifact chain

1. `Setup/draw-job.local.json`
2. `Setup/jobs/<job_name>/run-summary.json`
3. `Setup/jobs/<job_name>/analysis.json`
4. `Setup/jobs/<job_name>/plan.json`
5. `Setup/jobs/<job_name>/drawdsl.json`
6. `OutputPreview/<job_name>/round-*.png`
7. `OutputVSDX/<final>.vsdx`
8. `Setup/jobs/<job_name>/reviews/round-*.json`
9. `learningskills/lessons/*.md`

Do not skip the middle artifacts and hide all logic inside one script.

## 1. `draw-job.local.json`

Owner: `Setup`

Answers:
- which image is being drawn
- where outputs go
- how many rounds are allowed
- whether intermediate artifacts are kept

Should not contain:
- structure analysis
- layout rules
- direct Visio request sequences

## 2. `run-summary.json`

Owner: `Setup`

Answers:
- key job paths
- bridge readiness
- execution settings
- the current execution context for the run

This is the job index file, not the drawing plan.

## 3. `analysis.json`

Owner: `plannerskills`

Answers:
- what kind of figure this is
- which regions and element families exist
- what the visual risks are
- what remains uncertain
- which drawskills and visioskills capabilities are likely needed

Should not contain:
- precise Visio request sequences
- `session_id` or `shape_id`
- final pixel-perfect coordinates

## 4. `plan.json`

Owner: `plannerskills`

Consumers: `drawskills`, `visioskills`

Answers:
- what the drawing strategy is
- what must improve this round
- what constraints must hold
- what gets handed to drawskills and visioskills
- how the plan closes the loop from intent to operation to verification

Must contain:
- selected skills
- round objectives
- layout constraints
- style constraints
- capability plan
- handoff notes

### Capability plan

The `capability_plan` section is the key closed-loop structure.
Each item should map:

- drawing intent
- target region
- drawskills responsibilities
- visioskills operation bundle
- verification signals
- failure routing rules

This is how the project avoids blind retries.

## 5. `drawdsl.json`

Owner: `drawskills`

Answers:
- what the canvas is
- which nodes and edges exist
- where they go
- how big they are
- what text they contain
- what visual semantics they encode

Should not contain:
- bridge URL
- token
- request IDs
- session IDs

## 6. Preview PNG

Owner: `visioskills`

Purpose:
- let the agent see the current round result
- provide evidence for round review

## 7. Final `.vsdx`

Owner: `visioskills`

Purpose:
- the final deliverable Visio file

Retention is decided by `Setup`.

## 8. `reviews/round-*.json`

Owner: the round review step

Answers:
- what improved
- what is still wrong
- which layer owns each problem
- what the next round must do
- what findings may become lessons

This is round memory, not the long-term knowledge base.

## 9. `learningskills/lessons/*.md`

Owner: `learningskills`

Answers:
- what the reusable root cause was
- how to detect it earlier next time
- which layer should absorb the rule

Only reusable knowledge belongs here.

## Promotion rule

When you observe something:

- if it is only about this round, keep it in `reviews/round-*.json`
- if it may generalize but is not proven yet, keep it in review and watch another case
- if it generalizes cleanly, write a lesson
- if it is now a default rule, update the corresponding skill, reference, schema, or execution path
