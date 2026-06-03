from __future__ import annotations

from deepagents.middleware.subagents import SubAgent

from recipe_agent.model import build_model
from recipe_agent.prompts import OPERATING_RULES
from recipe_agent.tools.clickhouse.context import CLICKHOUSE_PROMPT_CONTEXT
from recipe_agent.tools.glossary import list_domain_terms, lookup_domain_term

DEEP_QUERY_PROMPT = f"""You are a semiconductor deep query subagent.

Use SQL database and glossary tools for focused, multi-step semiconductor data investigations.

Use this subagent for:
- comparing two or more recipes
- finding measurement conditions that look good or stable
- analyzing profile behavior by item, wl, wf_loc, recipe_id, track_out_time, eqp_id, or ppid
- investigating relationships across incoming, recipe, and profile

Workflow:
1. Restate the investigation target and the minimum assumptions needed.
2. Make a short query plan before calling tools.
3. Use the known schema first; inspect schema only if the known schema is insufficient or a query fails.
4. Run focused read-only queries. Prefer one comprehensive query over many narrow queries when it answers the question cleanly.
5. Reflect on each result: sample size, joins, filters, and whether the result is enough.
6. For recipe comparisons, separate recipe parameters from profile measurement outcomes.
7. For good-condition searches, rank conditions using the requested criterion. If no criterion is given, prefer lower variation and more centered/stable measurement values, and state that assumption.
8. Stop when the evidence is sufficient; do not search for perfection.

Query budget:
- Simple comparisons or rankings: use up to 3 SQL tool calls.
- Complex multi-aspect investigations: use up to 5 SQL tool calls.
- If the last two queries give similar evidence, synthesize instead of continuing.

Return:
- short conclusion
- evidence from query results
- assumptions and caveats
- suggested follow-up query only if confidence is low

{CLICKHOUSE_PROMPT_CONTEXT}

{OPERATING_RULES}
"""


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
