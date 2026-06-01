from __future__ import annotations

from recipe_agent.tools.clickhouse import describe_clickhouse_schema, query_clickhouse
from recipe_agent.tools.glossary import create_domain_term, list_domain_terms, lookup_domain_term

__all__ = [
    "create_domain_term",
    "describe_clickhouse_schema",
    "get_recipe_tools",
    "list_domain_terms",
    "lookup_domain_term",
    "query_clickhouse",
]


def get_recipe_tools():
    return [
        describe_clickhouse_schema,
        query_clickhouse,
        lookup_domain_term,
        list_domain_terms,
        create_domain_term,
    ]
