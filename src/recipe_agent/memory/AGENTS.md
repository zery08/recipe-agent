# Recipe Agent Memory

- Answer in Korean by default.
- Treat ClickHouse as read-only.
- Never run mutation, DDL, operational, or destructive SQL.
- Use glossary definitions for domain-specific recipe analytics terms.
- Prefer small exploratory queries before broad aggregations.
- For recipe comparisons, separate absolute values from rates and normalized metrics.
- State assumptions and data gaps when schema, metric definitions, or sample size are unclear.
