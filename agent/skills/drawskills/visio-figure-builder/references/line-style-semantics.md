# Line Style Semantics

Line style should encode meaning.

## Default mapping

- Solid dark line: normal structural connection
- Solid colored line: emphasized primary path
- Dashed line: auxiliary, reference, or implied relation
- Different arrowhead/color: feedback, annotation, or non-network I/O

## Rule

Do not use one uniform line style for every connector unless the source figure is intentionally uniform.

## Readability check

After export:

1. Can the reader tell primary flow from secondary relation?
2. Are dashed vs solid lines used consistently?
3. Are connectors visually competing with labels or boxes?
