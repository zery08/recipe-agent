from __future__ import annotations

import os
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv

from recipe_agent.model import build_model
from recipe_agent.prompts import SUPERVISOR_PROMPT
from recipe_agent.subagents import create_deep_query_subagent
from recipe_agent.tools.clickhouse import (
    clickhouse_describe_table,
    clickhouse_list_tables,
    clickhouse_query,
)
from recipe_agent.tools.glossary import (
    list_domain_terms,
    lookup_domain_term,
)

_PACKAGE_DIR = Path(__file__).resolve().parent

def create_recipe_agent():
    """Create the recipe analytics DeepAgent supervisor."""
    load_dotenv()

    backend = FilesystemBackend(root_dir=_PACKAGE_DIR, virtual_mode=True)
    supervisor_model = build_model("SUPERVISOR", temperature=0.0, streaming=True)
    tool_model = build_model("TOOL", temperature=0.0, streaming=True)

    tools = [ 
                clickhouse_query,
                clickhouse_list_tables,
                clickhouse_describe_table,
                lookup_domain_term,
                list_domain_terms
    ]

    return create_deep_agent(
        model=supervisor_model,
        tools=tools,
        system_prompt=SUPERVISOR_PROMPT,
        subagents=[
            create_deep_query_subagent(
                clickhouse_tools=clickhouse_tools,
                model=tool_model,
            )
        ],
        skills=["/skills"],
        memory=["/memory/AGENTS.md"],
        backend=backend,
    )


def create_agent():
    """Backward-compatible alias for the CLI."""
    return create_recipe_agent()
