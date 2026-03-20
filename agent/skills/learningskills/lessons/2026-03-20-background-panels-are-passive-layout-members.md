# Background Panels Are Passive Layout Members

## Trigger

The preview gets worse right after adding pale background subpanels that are only meant to visually group content.

## Problem

Modules that were previously in roughly correct positions get pushed far away, detail panels drift, and large blank areas appear even though the new shapes were only decorative subpanel backgrounds.

## Root Cause

The layout postprocess was treating large background rectangles as active participants in overlap cleanup and region separation. That makes the reflow logic respond to scaffolding instead of real content nodes.

## Reusable Fix

Mark decorative panel backgrounds with `role: "background"` and exclude them from row reflow, region separation, and residual overlap resolution. Keep them available for container auto-fit, but do not let them push other semantic nodes around.

For connector semantics, also keep reference links visually subordinate by default:

- gray instead of emphasis orange
- dashed instead of solid
- no arrowhead unless explicitly requested

## Where It Belongs

`drawskills`

## Example

In `inputpng-2`, adding DF-Mamba and SoftHistogram-DHSA background panels initially made the whole composition worse. After treating those panels as passive layout members, the overall page fit became more stable and the resulting preview was closer to the intended benchmark figure.
