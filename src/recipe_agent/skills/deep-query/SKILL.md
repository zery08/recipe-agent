---
name: deep-query
description: Use for multi-step semiconductor SQL investigations, including recipe comparison and good measurement-condition search.
---

# Deep Query Skill

Use this workflow for deep SQL investigations:

1. Restate the target: recipe comparison, condition search, trend check, or root-cause exploration.
2. Define the grain before querying: recipe, root_lot_id, root_lot_wafer_id, wl, wf_loc, item, or time window.
3. Use the known schema first; inspect schema only when the known schema is insufficient or a query fails.
4. Prefer one focused query that answers the question cleanly over several narrow queries.
5. Validate sample size, joins, and filters before drawing conclusions.
6. Keep the final answer scoped to the requested recipes, items, wordlines, locations, and time windows.

For recipe comparison:
- Join `incoming.recipe_id = recipe.recipe_id`.
- Join `incoming.root_lot_wafer_id = profile.root_lot_wafer_id`.
- Separate recipe parameters from profile measurement outcomes.

For good measurement-condition search:
- If the user gives a target, rank by closeness to that target.
- If no target is given, rank by lower variation and stable centered values.
- Measurement items such as `CD_IH` and `CD_OH` are stored in `profile.item`; measured numbers are in `profile.value`.

Do not add extra joins, filters, or dimensions unless they are needed for the question.
