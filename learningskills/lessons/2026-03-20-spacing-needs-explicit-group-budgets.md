# Spacing Needs Explicit Group Budgets

## Title

Do not treat spacing as a leftover cleanup step after nodes are placed.

## Trigger

The preview has no obvious text clipping, but the figure still feels cramped:

- titles touch nearby rows
- dashed containers sit too close to neighbors
- row and column clusters drift into each other
- local overlap cleanup keeps moving single nodes without improving the composition

## Problem

The agent can remove direct collisions and still produce a layout that does not read like a human-planned figure.

## Root Cause

The system only had:

- raw node coordinates
- local row or column gaps
- global overlap cleanup

That is not enough for whole-figure composition.
Important spatial intent was missing as a first-class artifact:

- which groups need breathing room
- which titles need reserved headroom
- which containers need padding beyond their members
- which regions should be separated before connector polish

## Reusable Fix

Represent spacing as an explicit drawskills budget, not only as coordinates:

1. Let `plannerskills` name the spatial intent.
2. Let `drawskills` emit `layout.groups` with:
   - `min_gap_x` and `min_gap_y`
   - `margin_left`, `margin_right`, `margin_top`, `margin_bottom`
3. Apply `layout.relations` on expanded group bounds, not only on bare member bounds.
4. Reserve title clearance and container padding through explicit constraints.
5. Review group spacing and title headroom separately from simple overlap detection.

## Where It Belongs

- `plannerskills`
- `drawskills`
- `learningskills`

## Example

In `inputpng-1`, adding group margins and title/container spacing defaults let the postprocess push the backbone band, neck rows, detail panels, and example lane apart as layout regions instead of repeatedly nudging individual boxes.
