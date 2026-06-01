from __future__ import annotations

from deepagents.middleware.subagents import SubAgent

from recipe_agent.model import build_model
from recipe_agent.prompts import RECIPE_COMPARE_PROMPT
from recipe_agent.tools.clickhouse import describe_clickhouse_schema, query_clickhouse
from recipe_agent.tools.glossary import list_domain_terms, lookup_domain_term

RECIPE_COMPARE_SUBAGENT: SubAgent = {
    "name": "recipe_compare",
    "description": (
        "Compare recipes deeply using read-only ClickHouse exploration, "
        "metric definitions, and recipe-domain glossary terms."
    ),
    "system_prompt": RECIPE_COMPARE_PROMPT,
    "model": build_model("TOOL", temperature=0.0, streaming=True),
    "tools": [
        describe_clickhouse_schema,
        query_clickhouse,
        lookup_domain_term,
        list_domain_terms,
    ],
    "skills": ["/skills"],
}
