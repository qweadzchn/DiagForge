# PREVIEW_REVIEW_CHECKLIST

Use this checklist when comparing a generated preview against the target figure.

The goal is not only to ask "did the font land?".
The goal is to catch the real visual failures that stop the drawing from looking human-made.

## 1. Region fit

- Are the major regions in the right places?
- Is the overall composition balanced like the source?
- Is the page size helping the layout rather than distorting it?
- Did the intended group margins and title headroom actually show up in the composition?

## 2. Box size and crowding

- Does each box size match its text amount?
- Did any text growth create collisions that were not reflowed?
- Are narrow modules still readable after layout compression?

## 3. Same-layer overlap

- Do peer nodes overlap each other?
- Are labels sitting on top of unrelated blocks?
- Is one module partially hiding another?

If yes, this is usually a `drawskills` failure unless the page itself is wrong.

## 4. Connector path shape

- Are row connectors mostly straight when the source is straight?
- Are vertical connectors mostly vertical when the source is vertical?
- Are connectors entering and leaving from sensible sides?
- Are there unnecessary folded or dogleg paths?
- If a connector was meant to be curved or orthogonal, does it actually read that way?

If the requested routing cells or glue-side controls did not land, this is `visioskills`.
If they landed but the paths are still semantically awkward, this is `drawskills`.

## 5. Labels and text-only shapes

- If a shape is acting as a text label, are its line and fill removed?
- Are transparent label shapes still causing visual stacking or obstruction?
- Is text placed inside the intended box when it belongs to that box?

## 6. Container correctness

- Do dashed outer containers actually wrap the intended group?
- Are titles aligned with the container they describe?
- Are unrelated nodes leaking into the wrong container area?

## 7. Fidelity details

- Which lines should be straight, curved, dashed, or emphasized?
- Which boxes should be tall, wide, narrow, or aligned as a repeated rhythm?
- Which source-specific details are simplified beyond acceptance?

## 8. Reflection

After each review, explicitly ask:

1. Which real problems did the previous review miss?
2. Why were they missed?
3. What check should be added so they are not missed again?

If the answer is a reusable rule, promote it into docs, schema, or lessons.
