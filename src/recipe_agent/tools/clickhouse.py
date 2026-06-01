from __future__ import annotations

import json
import re

_FORBIDDEN_SQL = re.compile(
    r"\b(ALTER|ATTACH|CREATE|DELETE|DETACH|DROP|EXCHANGE|INSERT|KILL|MOVE|OPTIMIZE|RENAME|REPLACE|SYSTEM|TRUNCATE|UPDATE)\b",
    re.IGNORECASE,
)

_SCHEMA_HINTS = {
    "recipes": [
        "recipes(recipe_id, recipe_name, category, created_at)",
        "recipe_events(recipe_id, event_date, views, clicks, conversions)",
        "recipe_costs(recipe_id, event_date, ingredient_cost, labor_cost)",
    ],
    "ingredients": [
        "recipe_ingredients(recipe_id, ingredient_id, ingredient_name, quantity, unit)",
        "ingredient_prices(ingredient_id, event_date, unit_cost)",
    ],
}


def _normalize_sql(sql: str) -> str:
    normalized = sql.strip().rstrip(";")
    if not normalized:
        raise ValueError("SQL is required.")
    if not normalized.lower().startswith(("select", "with")):
        raise ValueError("Only read-only SELECT/WITH queries are allowed.")
    if _FORBIDDEN_SQL.search(normalized):
        raise ValueError("Mutation or DDL statements are not allowed.")
    return normalized


def _with_limit(sql: str, limit: int) -> str:
    if re.search(r"\blimit\b", sql, flags=re.IGNORECASE):
        return sql
    return f"{sql}\nLIMIT {limit}"


def describe_clickhouse_schema(topic: str = "recipes") -> str:
    """Return known ClickHouse schema hints for recipe analytics."""
    normalized = topic.strip().lower() or "recipes"
    hints = _SCHEMA_HINTS.get(normalized) or _SCHEMA_HINTS["recipes"]
    return "\n".join(hints)


def query_clickhouse(sql: str, limit: int = 100) -> str:
    """Run a read-only ClickHouse query for recipe analytics.

    This is currently a guarded mock. Replace the marked section with a real
    ClickHouse client call when credentials and schema are finalized.
    """
    normalized_sql = _with_limit(_normalize_sql(sql), limit)

    # TODO: replace with clickhouse_connect.get_client(...).query(normalized_sql).
    result = {
        "status": "mock",
        "sql": normalized_sql,
        "rows": [],
        "note": "ClickHouse client is not wired yet. Query was validated as read-only.",
    }
    return json.dumps(result, ensure_ascii=False, indent=2)
