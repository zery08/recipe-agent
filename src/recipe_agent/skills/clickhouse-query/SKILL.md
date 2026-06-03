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

Known schema details are injected into system prompts from `tools/clickhouse/context.py`.
Treat that file as the canonical source for table columns, join keys, and schema notes.
