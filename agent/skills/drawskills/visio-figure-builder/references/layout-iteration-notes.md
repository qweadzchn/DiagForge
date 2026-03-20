# Layout Iteration Notes (Vortex-style network diagrams)

## Why previous version looked messy

1. Font-size unit mismatch can explode text and break composition.
2. Drawing connectors before alignment causes visual crossing/clutter.
3. Row spacing without consistent grid leads to drifting modules.
4. Too many near-saturated colors reduce readability.

## Iteration checklist

1. Build skeleton only (no connectors):
   - Place all blocks on lane grid
   - Align each row by `center_y`
   - Distribute each row horizontally
2. Validate text density:
   - 1-2 lines per node preferred
   - shrink long labels, not entire row
3. Add connectors in controlled order:
   - main pipeline
   - backbone chain
   - neck fusion links
   - module-detail links
4. Apply styling pass at end.

## Practical defaults

- Row gap: 1.1–1.4 in
- Same-row center spacing: 0.95–1.10 in
- Main block width: 2.4–3.2 in
- Module block width: 0.8–1.0 in

## Source-informed heuristics

Based on general diagram/figure design guidance:
- prioritize alignment, hierarchy, and whitespace
- keep typography consistent across full figure
- avoid decorative noise and excessive color saturation
