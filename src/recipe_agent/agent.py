from __future__ import annotations

from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from recipe_agent.model import build_model
from recipe_agent.prompts import SUPERVISOR_PROMPT
from recipe_agent.subagents import RECIPE_COMPARE_SUBAGENT
from recipe_agent.tools import get_recipe_tools

_PACKAGE_DIR = Path(__file__).resolve().parent


def create_recipe_agent():
    """Create the recipe analytics DeepAgent supervisor."""
    backend = FilesystemBackend(root_dir=_PACKAGE_DIR, virtual_mode=True)

    return create_deep_agent(
        model=build_model("SUPERVISOR", temperature=0.0, streaming=True),
        tools=get_recipe_tools(),
        system_prompt=SUPERVISOR_PROMPT,
        subagents=[RECIPE_COMPARE_SUBAGENT],
        skills=["/skills"],
        memory=["/memory/AGENTS.md"],
        backend=backend,
    )


def create_agent():
    """Backward-compatible alias for the CLI."""
    return create_recipe_agent()
