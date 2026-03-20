# Container Membership Cannot Come From Region Id Alone

## Trigger

A figure used more than one dashed container inside the same visual region, such as an outer graph box plus a smaller detect box.

## Problem

Review and auto-fit logic treated `region_id` as if it uniquely identified one container.
That breaks as soon as a region contains nested or sibling containers.

## Root Cause

`region_id` answers "which part of the figure is this node in?"
It does not answer "which container should wrap this node?"
Those are different questions.

## Reusable Fix

1. Support explicit `container_id` on nodes when the membership is known.
2. If `container_id` is missing, infer membership carefully from actual geometry.
3. Keep a separate signal for ambiguous cases instead of pretending the mapping is certain.
4. Let container auto-fit and container review use the same membership logic.

## Where It Belongs

- `drawskills` owns the structural intent and should emit `container_id` when possible.
- `Setup` / execution-time review may use careful fallback inference, but should report ambiguity.

## Example

In `inputpng-1`, `neck_container` and `detect_container` both belong to the `neck_graph` region.
Using only `region_id` made the smaller detect container look responsible for nodes that actually belonged to the larger neck graph.
Switching to container membership logic removed false container failures and made auto-fit usable.
