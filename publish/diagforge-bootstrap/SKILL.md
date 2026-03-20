---
name: diagforge-bootstrap
description: Bootstrap skill for DiagForge. Use this skill to onboard an agent into the DiagForge GitHub repository, understand the project structure, run the canonical cold-start smoke test, and begin working with the Visio-based drawing loop safely.
version: 0.1.0
metadata:
  openclaw:
    homepage: https://github.com/qweadzchn/DiagForge
    requires:
      bins:
        - git
        - python
      env:
        - VISIO_BRIDGE_TOKEN
---

# DiagForge Bootstrap

This is a lightweight onboarding skill for the DiagForge repository.

It is not the full DiagForge system.
Its job is to guide an agent to the correct GitHub repository, documents, smoke test, and execution flow.

## What this skill is for

Use this skill when an agent needs to:

- find the DiagForge source repository
- understand the top-level architecture quickly
- avoid free-form blind retries
- run the canonical cold-start smoke test
- begin work in the correct layer

## What this skill is not

This skill does not bundle the whole repository.
It does not include Visio bridge code, benchmark PNGs, or runtime artifacts.

The full project lives in the GitHub repository:

`https://github.com/qweadzchn/DiagForge`

## Recommended workflow

1. Clone the GitHub repository locally.
2. Read the cold-start entry documents.
3. Run the canonical smoke test before doing open-ended drawing work.
4. Only then move on to real jobs or system improvements.

## Clone the repository

```bash
git clone git@github.com:qweadzchn/DiagForge.git
cd DiagForge
```

If SSH is not available, use HTTPS instead.

## Read order

Read these files first:

1. `AGENT_START_HERE.md`
2. `AGENT_GUIDE.md`
3. `GET_STARTED.md`
4. `docs/human/setup/AGENT_COLD_START_SMOKE_TEST.md`
5. `MODE_POLICY.md`

## Canonical smoke test

From the repo root:

```powershell
python Setup\prepare_smoke_test.py --config Setup\examples\smoke-test-inputpng-1.json
python Setup\run_draw_job.py --config Setup\examples\smoke-test-inputpng-1.json
python Setup\execute_drawdsl.py --config Setup\examples\smoke-test-inputpng-1.json --round 1 --save-final
```

Expected outputs:

- `OutputPreview/smoke-inputpng-1/round-01.png`
- `OutputEditable/1_smoke_test_final.vsdx`

## Routing rule

When working inside DiagForge:

- if the issue is round-specific, keep it in review artifacts
- if it looks structural but still needs validation, write a proposal
- if it is already reusable experience, promote it into a lesson
- if the shared fix is clear, patch the owning layer directly

## Where to go next

See:

- `README.md`
- `CONTRIBUTING.md`
- `docs/architecture/FEEDBACK_PROMOTION_LOOP.md`
