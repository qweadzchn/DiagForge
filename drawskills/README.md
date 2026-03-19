# drawskills

`drawskills` owns the question:

"How do we turn a drawing plan into a clear, readable, well-spaced figure?"

It is the layout and figure-construction layer.
It is not the orchestration layer and not the Visio runtime layer.

## This layer decides

- font size bands
- box growth rules
- text direction
- spacing and local reflow
- group margins, title bands, and container padding
- container sizing
- connector semantics
- connector route intent
- DrawDSL output

## This layer does not decide

- what kind of figure the source image is
- which task is running
- how the bridge talks to Visio COM
- which one-off lesson should become long-term knowledge

## Main artifact

- `Setup/jobs/<job>/drawdsl.json`

## Important files

- `schemas/drawdsl.schema.json`
- `layout_postprocess.py`
- `visio-figure-builder/SKILL.md`

## Current built-in drawing rules

- Times New Roman is the default font family
- text size, box size, and gap are coupled
- vertical text is allowed when it improves narrow-module readability
- vertical text also requires text-block synthesis and local reflow
- overall spacing should be expressed as explicit `layout.groups` plus `layout.relations`, not only as raw coordinates
- group bounds may reserve outer margins for title clearance and inter-region breathing room
- container sizing should come from actual grouped content, not just fixed coordinates
- line routing should be planned as intent such as `straight_horizontal`, `straight_vertical`, `orthogonal`, or `curved`
- same-layer overlap should be treated as a failure by default

## Boundary reminder

If the preview still looks wrong after the requested Visio cells landed correctly, the next fix usually belongs here.
