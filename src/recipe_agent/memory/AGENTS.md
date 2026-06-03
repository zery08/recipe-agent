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
- Use the ClickHouse prompt context in `tools/clickhouse/context.py` as the canonical source for table columns, joins, and schema notes.
- Do not guess schema, joins, or metric meanings.
- Ask a short clarification only when ambiguity blocks a correct query; otherwise state the assumption and continue.
- Keep SQL and analysis scoped to the user's request.
- Validate query results before summarizing, especially empty or surprising results.
