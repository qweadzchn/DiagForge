# Text Layout Coupling

These are default constraints for readable Visio diagrams.

## Core Rule

Text size, box size, and spacing are coupled.

Do not change one without reconsidering the other two.

## Required behavior

1. If font size increases:
   - increase box width or height as needed
   - re-check neighboring gaps
2. If text wraps into more lines:
   - grow height before shrinking text
3. If text rotates vertically:
   - recalculate width/height assumptions
   - re-check lane spacing
4. If text becomes unreadable:
   - prefer growing the box and row spacing before shrinking typography

## Practical defaults

- Use `Times New Roman`
- Keep main titles clearly larger than body labels
- Reserve padding inside boxes; do not let text touch borders
- Prevent any two boxes from visually colliding after text expansion
