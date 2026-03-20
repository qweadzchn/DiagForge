# Reference links need stronger routing guardrails

## Status

proposed

## Summary

Reference-style links and long orthogonal connectors need stronger planning and verification guardrails so they do not sprawl across the page even when execution succeeds mechanically.

## Why this matters

Current execution can land the requested connectors, but the visual result can still be poor.
This creates a false sense of success unless review and planning both treat routing span as a first-class quality target.

## Evidence

- `Setup/jobs/inputpng-2/reviews/round-04-execution.json` reported multiple connector geometry warnings.
- The warnings include large connector width or height and large reference-link spans such as `e_center_ref`, `e_gmsf_ref`, and `e_fftb_ref`.
- This suggests that route intent alone is not yet enough for long cross-region explanation links.

## Suspected owner layer

- `drawskills`
- `visioskills`
- `mixed`

## Proposed change shape

Improve the closed loop for reference links by combining:

- planner-level declaration that a connector is a reference or annotation link
- drawskills spacing and anchor rules for those links
- visioskills-side geometry verification with clearer failure routing

The main goal is to detect "execution landed but still visually wrong" earlier and more consistently.

## Validation plan

Use at least two diagrams with long cross-region explanation links and confirm that:

- geometry warnings decrease
- reference links keep readable span and direction
- the next round knows whether to fix routing intent, anchors, or local spacing

## Promotion trigger

Promote this into a lesson or default rule after the project shows improved behavior on multiple benchmark jobs.
Reject or narrow it if the issue turns out to belong only to one benchmark layout.
