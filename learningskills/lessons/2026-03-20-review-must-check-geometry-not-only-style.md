# Review Must Check Geometry Not Only Style

## Title

Do not treat successful Visio cell writeback as proof that the drawing is visually correct.

## Trigger

The execution log shows fonts, arrows, and line weights landed correctly, but the preview still looks obviously wrong: modules overlap, containers miss their content, labels block shapes, or connectors read awkwardly.

## Problem

A review can become too execution-centric and miss the real visual defects that a human would notice immediately.

## Root Cause

The system checked whether requested operations succeeded, but did not separately check geometric fidelity:

- same-layer overlap
- box crowding
- outer-container coverage
- connector path shape
- whether text-only nodes are visually transparent

## Reusable Fix

Every serious review should combine two kinds of evidence:

1. execution evidence
   - font landed
   - arrow settings landed
   - routing cells landed
2. geometry evidence
   - no unintended overlap
   - containers wrap the intended group
   - connectors follow the expected visual path
   - label nodes are transparent when used as text-only shapes

If execution is clean but geometry is bad, route the fix to `drawskills` or `plannerskills`, not back to `visioskills`.

## Where It Belongs

- `drawskills`
- `learningskills`

## Example

In `inputpng-1`, earlier rounds correctly applied Times New Roman and connector styles, but the review still missed RAW overlapping the main model block and Box Draw overlapping NMS. Adding geometry checks exposed those failures immediately.
