from __future__ import annotations

CLICKHOUSE_PROMPT_CONTEXT = """Known database schema:

Tables:
- incoming(root_lot_wafer_id, root_lot_id, wafer_id, track_out_time, recipe_id, eqp_id, ppid)
- recipe(recipe_id, step_no, step_name, param_key, value, unit)
- profile(root_lot_wafer_id, root_lot_id, wl, wf_loc, item, value, unit, measured_at)

Join keys:
- incoming.root_lot_wafer_id = profile.root_lot_wafer_id
- incoming.recipe_id = recipe.recipe_id

Domain notes:
- root_lot_wafer_id is the wafer-level key.
- incoming contains wafer-level track-out metadata and the recipe_id used on that wafer.
- recipe contains step-level recipe parameters; param_key names the parameter and value stores the numeric setting.
- profile contains measurement values. Measurement item names such as CD_IH and CD_OH are stored in profile.item; the measured number is profile.value.

Schema tool policy:
- Use the known schema above first.
- Do not call table-list or schema-inspection tools before every SQL query.
- Call schema-inspection tools only when the user asks for unknown schema details, the requested column/table is not in the known schema, or a query fails because of a schema mismatch.
- If the known schema is enough, write the SQL directly.
"""
