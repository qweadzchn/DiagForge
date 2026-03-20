# PLAN_TO_OPERATION_LOOP

This document explains how a planner turns "what we want" into "what the agent will do and how the result will be judged".

## Why this exists

Bad drawing loops often fail in one of two ways:

1. The plan is too abstract, so execution becomes guesswork.
2. The execution is explicit, but nobody knows what should be checked or where failures belong.

The `capability_plan` section in `plan.json` exists to prevent both problems.

## One capability item should answer

1. What drawing intent matters here?
2. Which region does it affect?
3. What decisions belong to drawskills?
4. Which visioskills operations are expected?
5. Which signals prove success?
6. If those signals fail, which layer owns the fix?

For spacing-heavy figures, the plan should also make one thing explicit:

- `plannerskills` names the spatial intent:
  which regions stay apart, which titles need headroom, which lanes align, which connector families should be straight or curved
- `drawskills` realizes that intent:
  `layout.groups`, `layout.relations`, group margins, title clearance, container padding, and `route_intent`
- `visioskills` lands the requested controls:
  pins, route cells, geometry writes, and readback

## Template

```json
{
  "intent_id": "narrow-module-readability",
  "intent_summary": "Keep narrow modules readable without collapsing the row.",
  "target_region": "backbone_row",
  "drawskills_responsibilities": [
    "Choose width bands",
    "Choose font bands",
    "Add line breaks when needed"
  ],
  "visioskills_operations": [
    "shape/add",
    "shape/set_text_style",
    "shape/describe"
  ],
  "verification_signals": [
    "Labels are readable in preview",
    "Font landed in readback",
    "Boxes do not clip text"
  ],
  "failure_routing": [
    {
      "signal": "Font did not land in readback",
      "owner_layer": "visioskills",
      "action": "Fix the text-style write path"
    },
    {
      "signal": "Font landed but row still collapses",
      "owner_layer": "drawskills",
      "action": "Rebalance box widths and spacing"
    }
  ]
}
```

## Writing rules

- Keep one item focused on one drawing intent.
- Do not hide verification inside vague phrases like "looks better".
- Prefer signals that can be checked in preview, execution log, or readback.
- Route failure to the layer that can actually fix it.
- If repeated failures create a general rule, promote that rule into `learningskills` or a layer reference.

## Quick routing guide

- If the requested Visio operation did not land, it is usually `visioskills`.
- If the operation landed but the drawing still looks wrong, it is usually `drawskills`.
- If the wrong region or priority was chosen, it is usually `plannerskills`.
- If the same root cause appears across jobs, it should also become `learningskills`.
