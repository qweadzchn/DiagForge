# Page Fit And Glue Side Before Layout Judgment

## Title

Resize the page and choose connector attachment sides before judging whether a figure is badly planned.

## Trigger

The preview looks squeezed, vertically stretched, or full of awkward connector detours even though node coordinates and style settings seem reasonable.

## Problem

It is easy to misdiagnose these previews as pure drawskills layout failures and keep nudging positions, font sizes, or gaps without real progress.

## Root Cause

Two lower-level execution issues can create fake layout defects:
1. The figure is being forced into Visio's default page instead of a page that fits the content.
2. Connectors are gluing through shape centers instead of the sides that match the intended flow direction.

## Reusable Fix

Before a serious review round:
1. Read the current page size.
2. Resize the page to content bounds plus margin.
3. Infer or specify connector glue sides from relative geometry.
4. Read back fonts and connector styles to confirm they actually landed.
5. Only then decide which remaining issues belong to drawskills or plannerskills.

## Where It Belongs

- `visioskills`
- `drawskills`
- `learningskills`

## Example

In `inputpng-1`, early previews looked cramped and connector-heavy. After adding page auto-fit and glue-side control, style readback showed zero execution mismatches, and the remaining defects became clearly attributable to drawskills-level cluster layout instead of bridge instability.
