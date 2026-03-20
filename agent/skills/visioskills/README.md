# visioskills

`visioskills` owns the question:

"How do we operate Visio reliably and verifiably?"

It is the execution layer.
It should stay explicit, atomic, and boring.

## This layer owns

- session lifecycle
- shape creation and geometry updates
- connector creation
- page sizing
- text/style writes
- artifact export
- shape readback

## This layer does not own

- diagram meaning
- layout taste
- figure planning
- long-term lessons

## Important files

- `bridge_server/app.py`
- `bridge_server/visio_adapter.py`
- `client/http_client.py`
- `OPERATIONS.md`
- `visio-operator/SKILL.md`

## Recent useful capabilities

- page-size readback and setup
- connector glue-side control
- connector style readback
- transparent label support
- text rotation through `TxtAngle`
- font readback for verification

## Boundary reminder

If the intended Visio operation did not actually land, fix it here.
If it landed and the picture still looks wrong, the next fix usually belongs in `drawskills` or `plannerskills`.
