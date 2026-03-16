---
name: visio-figure-builder
description: Build publication-style figures in Microsoft Visio through the png2vsdx bridge. Use when asked to draw/reproduce/edit diagrams in Visio, especially for research papers. Always remind the user to start the Windows Visio bridge service before execution, then compile high-level drawing intents into visioskills atomic calls.
---

# Visio Figure Builder

## Preflight (mandatory)

1. Remind user to start Windows bridge service first:
   - `uvicorn bridge_server.app:app --host <windows-wsl-ip> --port 18761`
2. Verify from WSL:
   - `GET /health`
   - `POST /ping_visio`
3. Stop and ask user to fix runtime if either check fails.

## Default style preset (research baseline)

- Font family: **Times New Roman**
- Font size: **11 pt** (title inside node can be 12 pt)
- Text color: `RGB(20,20,20)`
- Line color: `RGB(40,40,40)`
- Line weight: `1.0~1.4 pt`
- Fill color: light neutral/pastel (avoid high saturation)
- Spacing: keep consistent horizontal/vertical gaps

## Execution pipeline

1. Parse intent to DrawDSL structure (nodes, edges, layout, style).
2. Emit visioskills calls in strict order:
   - `session/create`
   - `shape/add` (all nodes)
   - `shape/update_geometry`
   - `shape/set_text_style` (Times New Roman unless explicitly overridden)
   - `shape/set_text_block` (if label needs positioning)
   - `shape/set_colors`
   - `shape/connect`
   - `session/save`
3. Report created shape IDs and save path.

## Atomic operation mapping

- Add node -> `/shape/add`
- Move/resize -> `/shape/update_geometry`
- Text/font/size/color -> `/shape/set_text_style`
- Text region position -> `/shape/set_text_block`
- Border/fill/line width -> `/shape/set_colors`
- Link nodes -> `/shape/connect`

## Failure policy

- If 5xx on one operation, retry once with same `request_id` semantics respected by caller.
- If still failing, return exact failed step and payload summary.
- Prefer explicit `save_path` in `/session/save` to avoid unnamed document save edge cases.

## Reproduction workflow (when user provides an example figure)

1. Extract graph topology first (nodes + arrows).
2. Reproduce layout with rough coordinates.
3. Apply style pass (font, color, line width, fill).
4. Apply polish pass (alignment, spacing, text block adjustments).
5. Save and show concise diff notes vs target.

## Use references

- For color/typography presets and journal-facing defaults, read:
  - `references/research-figure-guidelines.md`
