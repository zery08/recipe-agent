from __future__ import annotations

import sys

from rich.console import Console

from recipe_agent.observability import setup_observability
from recipe_agent.streaming import stream_answer


def main() -> None:
    setup_observability()

    from recipe_agent.agent import create_recipe_agent

    console = Console()
    error_console = Console(stderr=True)
    agent = create_recipe_agent()

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        stream_answer(agent, question, console=console, error_console=error_console)
        return

    console.print("Recipe Agent CLI. Type 'exit' to quit.")
    while True:
        try:
            question = console.input("\n[bold cyan]>[/] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            return

        if question.lower() in {"exit", "quit", "q"}:
            return

        if not question:
            continue

        stream_answer(agent, question, console=console, error_console=error_console)
