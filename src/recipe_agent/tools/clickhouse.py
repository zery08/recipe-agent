from __future__ import annotations

import os
from functools import lru_cache

from langchain_core.tools import tool
from sqlalchemy import create_engine, inspect, text


@lru_cache(maxsize=1)
def get_engine():
    uri = os.getenv("CLICKHOUSE_URI")
    if not uri:
        raise RuntimeError("CLICKHOUSE_URI environment variable is not set.")
    return create_engine(uri)


@tool(
    description=(
        "Run a read-only SQL query against ClickHouse. "
        "Only SELECT, WITH, SHOW, DESCRIBE, and DESC queries are allowed. "
        "Use this for normal data retrieval."
    )
)
def clickhouse_query(sql: str) -> str:
    sql_clean = sql.strip()
    sql_lower = sql_clean.lower()

    allowed = ("select", "with", "show", "describe", "desc")

    if not sql_lower.startswith(allowed):
        raise ValueError("Only read-only queries are allowed.")

    engine = get_engine()

    with engine.connect() as conn:
        result = conn.execute(text(sql_clean))
        rows = result.fetchmany(100)

    return "\n".join(str(row) for row in rows)


@tool(
    description=(
        "List ClickHouse tables in the current database. "
        "Use this only when the table names are unknown."
    )
)
def clickhouse_list_tables() -> str:
    engine = get_engine()

    with engine.connect() as conn:
        insp = inspect(conn)
        tables = insp.get_table_names()

    return "\n".join(tables)


@tool(
    description=(
        "Describe columns and types of a ClickHouse table. "
        "Use this when schema details are needed before writing SQL."
    )
)
def clickhouse_describe_table(table_name: str) -> str:
    engine = get_engine()

    with engine.connect() as conn:
        insp = inspect(conn)
        columns = insp.get_columns(table_name)

    return "\n".join(
        f"{col['name']} {col['type']}"
        for col in columns
    )
