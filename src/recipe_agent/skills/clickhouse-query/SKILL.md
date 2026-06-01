---
name: clickhouse-query
description: Use when answering recipe analytics questions that require read-only ClickHouse queries.
---

# ClickHouse Query Skill

Use this workflow for ClickHouse-backed recipe analytics:

1. Clarify the metric, grain, filters, and time window.
2. Check glossary terms before using domain-specific metric names.
3. Inspect schema hints before writing a query.
4. Use only read-only `SELECT` or `WITH` queries.
5. Add a `LIMIT` for exploratory row-returning queries.
6. Summarize assumptions, filters, and data caveats with the result.

Never run mutation, DDL, or operational statements.
