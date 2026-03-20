# New agent cold start needs a canonical smoke test

## Status

implemented

## Summary

DiagForge should have a documented and repeatable cold-start smoke test that a newly arrived agent can run before attempting open-ended diagram work.

## Why this matters

The repo is trying to be agent-friendly, not only executable by an already-contextualized maintainer.
Without a canonical smoke test, it is hard to tell whether a failure comes from onboarding gaps, environment gaps, missing artifacts, or drawing logic.

## Evidence

- `InputReference/1.png` and `InputReference/2.png` could be executed end-to-end only after reusing existing `analysis.json`, `plan.json`, and `drawdsl.json` workspaces.
- The preflight and execution chain is healthy, but "brand-new image to good artifacts" is still not a one-command turnkey path.
- A first-time agent benefits from a known-good validation route before attempting structural improvements.

## Suspected owner layer

- `Setup`
- `docs/contracts`
- `mixed`

## Proposed change shape

Add a canonical smoke-test definition for newly arrived agents that answers:

- which config to copy
- which benchmark job to run first
- which outputs must appear
- what counts as a passing environment
- what this test does not prove yet

This can stay lightweight and documentation-first at first.

## Validation plan

Ask a freshly started agent to use the documented smoke test without hidden context.
The test should be considered successful if the agent can:

- run preflight
- execute one known-good benchmark job
- find preview and VSDX outputs
- explain what still remains outside the smoke-test scope

## Promotion trigger

Promote this into a shared default onboarding rule if multiple fresh-agent sessions benefit from it.
Reject or rewrite it if the repo later gains a stronger fully automated cold-start pipeline.
