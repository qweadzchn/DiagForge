# visioskills operations (v0.3)

Principle: one API should do one verifiable Visio action well. Keep operations atomic, idempotent, and explicit.

## Stable capabilities

### Session
- `POST /session/create`
  - Create or open a Visio document session.
- `POST /session/save`
  - Save the current document, optionally to an explicit `save_path`.
- `POST /session/close`
  - Close the current session.

### Shapes
- `POST /shape/add`
  - Add a shape.
  - Stable shape types today: `Rectangle`, `Circle`, `Line`.
- `POST /shape/select`
  - Select a shape explicitly.
- `POST /shape/update_geometry`
  - Update position and size.
- `POST /shape/align`
  - Align multiple shapes.
- `POST /shape/distribute`
  - Distribute multiple shapes.
- `POST /shape/connect`
  - Add a connector between two shapes.
  - Supports optional `from_pin_x`, `from_pin_y`, `to_pin_x`, `to_pin_y` so the agent can choose which side of each shape the connector attaches to.
- `POST /shape/describe`
  - Read back geometry, text, font, line weight, arrowheads, connector endpoints, and selected route cells.

### Page
- `POST /page/info`
  - Read the current page size.
- `POST /page/setup`
  - Resize the page before drawing so wide figures do not get crushed into the default portrait page.

### Styling
- `POST /shape/set_text_style`
  - Set text, font family, font size, text color, and optional text rotation.
  - Supports `text_direction` and `text_angle_deg` so narrow modules can use vertical text.
- `POST /shape/set_text_block`
  - Adjust the text block position and size.
- `POST /shape/set_colors`
  - Set line color, fill color, line weight, line pattern, fill pattern, rounding, and arrowheads.
  - Also supports raw route-control cells such as `ShapeRouteStyle` and `ConLineRouteExt`.

Upstream note:
- Whether a connector should be `straight_horizontal`, `straight_vertical`, `orthogonal`, or `curved` is a `drawskills` decision.
- `visioskills` only exposes the low-level controls needed to land that routing intent.

### Preview and artifacts
- `POST /session/export_png`
  - Export the current page as PNG for closed-loop review.
- `GET /artifact/download/{ticket}`
  - Download an exported artifact with a one-time ticket.

## Usage constraints

### Auth
- Use `Authorization: Bearer <token>`.

### Idempotency
- Every write request must carry a `request_id`.
- Retries should reuse the same `request_id`.

### Explicit targeting
- Prefer explicit `session_id`, `shape_id`, and `page_name`.
- Do not rely on implicit UI selection state.

## Boundary

`visioskills` answers "how do we operate Visio reliably?"

It does not decide:
- what the figure means
- what the final layout should be
- what aesthetic tradeoffs to make
- what lessons should become reusable policy

Those belong to `plannerskills`, `drawskills`, and `learningskills`.

## Current gaps

Still missing or weak:
- relationship readback at graph level, not just single-shape inspection
- higher-level editing such as duplicate, group, ungroup, delete, and z-order
- richer connector routing policy beyond low-level cells and glue-side control
- image placement and richer master/stencil usage

## Recommended order

1. `health`
2. `ping_visio`
3. `session/create`
4. `page/info`
5. `page/setup` if needed
6. `shape/add`
7. `shape/update_geometry` / `shape/align` / `shape/distribute`
8. `shape/connect`
9. `shape/set_text_style` / `shape/set_text_block` / `shape/set_colors`
10. `shape/describe` for readback
11. `session/export_png`
12. `session/save`

## Maintenance rule

Before adding a new operation, check:
1. Is it atomic enough?
2. Is it idempotent and explicitly targetable?
3. Does it truly belong in `visioskills`, or should it stay in planner/draw policy instead?
