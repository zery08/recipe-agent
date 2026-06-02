# Recipe Agent Memory

- Answer in Korean by default.
- Treat ClickHouse as read-only.
- Never run mutation, DDL, operational, or destructive SQL.
- Use glossary definitions for domain-specific recipe analytics terms.
- Treat glossary terms as read-only validated context; do not create or mutate glossary entries during a run.
- Prefer small exploratory queries before broad aggregations.
- For deep query tasks, separate recipe parameters from profile measurement outcomes.
- Use `deep_query` for multi-step investigations such as comparing recipes or finding good measurement conditions.
- State assumptions and data gaps when schema, metric definitions, or sample size are unclear.
- Test schema join key is `root_lot_wafer_id` between `incoming` and `profile`.
- `incoming` has wafer-level metadata: `root_lot_wafer_id`, `root_lot_id`, `wafer_id`, `track_out_time`, `recipe_id`, `eqp_id`, `ppid`.
- `recipe` has recipe parameters: `recipe_id`, `step_no`, `step_name`, `param_key`, `value`, `unit`.
- `profile` has measurements: `root_lot_wafer_id`, `root_lot_id`, `wl`, `wf_loc`, `item`, `value`, `unit`, `measured_at`.
- Do not guess schema, joins, or metric meanings.
- Ask a short clarification only when ambiguity blocks a correct query; otherwise state the assumption and continue.
- Keep SQL and analysis scoped to the user's request.
- Validate query results before summarizing, especially empty or surprising results.
