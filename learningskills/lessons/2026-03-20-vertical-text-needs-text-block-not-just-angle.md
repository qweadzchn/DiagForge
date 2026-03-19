# Vertical Text Needs Text Block, Not Just Angle

## Trigger

A narrow module switched from wrapped horizontal text to vertical text, but the letters still looked cramped or stacked awkwardly.

## Problem

Setting only `TxtAngle` is not enough.
The text can still wrap against the old text block dimensions, which makes the result look machine-ish instead of human-adjusted.

## Root Cause

Text orientation and text block geometry are coupled.
When text rotates, the effective width and height of the text block need to rotate too.

## Reusable Fix

When a node uses vertical text:

1. Rotate the text with `TxtAngle`.
2. Normalize the text so old manual line breaks do not fight the new orientation.
3. Recompute the box size.
4. Recompute the text block dimensions so `TxtWidth` tracks the tall axis and `TxtHeight` tracks the narrow axis.
5. Re-run local spacing checks after the box changes.

## Where It Belongs

- `visioskills` owns the ability to write and read back `TxtAngle`.
- `drawskills` owns the decision to use vertical text and the matching text-block/layout reflow.

## Example

In `inputpng-1`, rotating `AMSP-VC`, `Upsample`, and `FAD-CSP` without adjusting the text block produced cramped vertical lettering.
Adding automatic vertical text-block synthesis made the labels read much closer to the source figure.
