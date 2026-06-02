from __future__ import annotations

from deepagents.middleware.subagents import SubAgent

from recipe_agent.model import build_model
from recipe_agent.prompts import DEEP_QUERY_PROMPT
from recipe_agent.tools.glossary import list_domain_terms, lookup_domain_term


def create_deep_query_subagent(
    *,
    clickhouse_tools=None,
    model=None,
) -> SubAgent:
    return {
        "name": "deep_query",
        "description": (
            "Use for multi-step SQL investigations over incoming, recipe, and "
            "profile data: compare recipes, find good measurement conditions, "
            "or analyze relationships across recipe parameters and profile "
            "measurements."
        ),
        "system_prompt": DEEP_QUERY_PROMPT,
        "model": model or build_model("TOOL", temperature=0.0, streaming=True),
        "tools": [
            *(clickhouse_tools or []),
            lookup_domain_term,
            list_domain_terms,
        ],
        "skills": ["/skills"],
    }
