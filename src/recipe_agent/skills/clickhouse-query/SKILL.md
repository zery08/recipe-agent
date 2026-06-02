---
name: clickhouse-query
description: Use when answering recipe analytics questions that require read-only ClickHouse queries.
---

# ClickHouse Query Skill

Use this workflow for ClickHouse-backed recipe analytics:

1. Clarify the metric, grain, filters, and time window.
2. Check glossary terms before using domain-specific metric names.
3. Use the known schema first; inspect schema only when the known schema is insufficient or a query fails.
4. Use only read-only `SELECT` or `WITH` queries.
5. Add a `LIMIT` for exploratory row-returning queries.
6. Summarize assumptions, filters, and data caveats with the result.

Never run mutation, DDL, or operational statements.
Do not add extra joins, filters, columns, or analysis unless they are needed for the question.
If ambiguity blocks a correct query, ask one short clarification question; otherwise state the assumption and continue.
If a query returns empty or surprising results, check whether filters or joins caused it before summarizing.

Test schema:
- `incoming(root_lot_wafer_id, root_lot_id, wafer_id, track_out_time, recipe_id, eqp_id, ppid)`
- `recipe(recipe_id, step_no, step_name, param_key, value, unit)`
- `profile(root_lot_wafer_id, root_lot_id, wl, wf_loc, item, value, unit, measured_at)`

Use `root_lot_wafer_id` to join `incoming` and `profile`; use `recipe_id` to join `incoming` and `recipe`.
