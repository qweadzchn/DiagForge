# Route Shape Must Be An Explicit Intent

## Title

Connector shape should be planned as intent, not guessed only from generic line style.

## Trigger

The preview shows that some lines should clearly be straight horizontal, straight vertical, orthogonal, or curved, but the system only writes generic connector style cells and hopes Visio chooses well.

## Problem

Even when arrowheads and line weights land correctly, connector paths can still look wrong:

- horizontal chains become folded
- vertical links become wide doglegs
- skip links lose their curved character

## Root Cause

The drawing plan encoded connector importance, but not connector path intent.
That left the executor without a stable way to distinguish:

- straight horizontal
- straight vertical
- orthogonal
- curved

## Reusable Fix

Add `route_intent` to DrawDSL edges and keep the ownership split clear:

1. `drawskills` decides the intended route family.
2. `visioskills` applies the low-level route cells and glue-side controls needed to land it.
3. Review compares the exported geometry against the intended route family, not only against whether arrow cells landed.

## Where It Belongs

- `drawskills`
- `visioskills`
- `learningskills`

## Example

In `inputpng-1`, the executor now resolves route intent per edge and records it in the execution log, so straight row chains, vertical downlinks, and curved skip links can be reviewed as different connector behaviors.
