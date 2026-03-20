# plannerskills

This directory owns the question:
"What is this figure, what matters in it, and how should the work be staged?"

It is the orchestration layer.
It does not directly operate Visio.

## Core questions

When the input is a new image, plannerskills should answer:

1. What kind of diagram is this?
2. Which regions, groups, and priorities exist?
3. Which elements are primary flow and which are supporting explanation?
4. Which drawskills are needed?
5. Which visioskills controls are needed?
6. How will we verify that the important intents were actually achieved?
7. If verification fails, which layer should own the fix?

## Standard outputs

- `analysis.json`
- `plan.json`

If those do not exist, the agent should not jump straight into a complex drawing run.

## What `plan.json` must do

The plan is not only a strategy memo.
It must bridge all the way from intent to execution to review.

That means the plan should include:

- drawing strategy
- round objectives
- layout constraints
- style constraints
- spatial intent for major groups and lanes
- handoff to drawskills
- handoff to visioskills
- capability plan

For spacing-heavy figures, the planner should name:

- which groups must stay visually separate
- which titles need reserved headroom
- which lanes should read as rows, columns, or stacked regions
- which connector families should prefer straight, orthogonal, or curved routing

The planner names these intents.
`drawskills` turns them into concrete margins, gaps, group relations, and route intent in DrawDSL.

## Capability plan rule

For each important drawing intent, plannerskills should specify:

- what the intent is
- which region it affects
- what drawskills must decide
- which visioskills operations are expected
- how success will be checked
- how failure will be routed

Example:

- Intent: keep arrows directional and readable
- Drawskills: assign connector semantics and route expectations
- Visioskills: `shape/connect`, `shape/set_colors`, `shape/describe`
- Verification: arrowheads visible, line weight strong enough, connector attaches from sensible side
- Failure routing:
  - if arrow cells did not land -> `visioskills`
  - if they landed but still read badly -> `drawskills`

## Boundary

plannerskills may:
- decide sequence
- decide priorities
- decide required capabilities
- decide what review should check

plannerskills may not:
- hardcode Visio runtime request sequences
- own final geometry and styling details
- silently absorb execution-layer failures as planning problems
