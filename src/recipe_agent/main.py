from __future__ import annotations

import sys
from typing import Iterable

from rich.console import Console

from recipe_agent.observability import setup_observability


def _safe_iter_projection(projection) -> Iterable[str]:
    if projection is None:
        return []
    return projection


def _print_projection(
    console: Console,
    projection,
    *,
    prefix: str,
    style: str | None = None,
) -> None:
    for index, value in enumerate(_safe_iter_projection(projection)):
        if index == 0:
            console.print(prefix, end="", style=style)
        console.print(value, end="", style=style)


def stream_answer(
    agent,
    question: str,
    *,
    console: Console | None = None,
) -> None:
    console = console or Console()

    payload = {"messages": [{"role": "user", "content": question}]}
    stream = agent.stream_events(payload, version="v3")

    for name, item in stream.interleave("messages", "tool_calls"):
        if name == "messages":
            _print_projection(
                console,
                getattr(item, "reasoning", None),
                prefix="\n[thinking] ",
                style="dim yellow",
            )
            _print_projection(console, getattr(item, "text", None), prefix="\n[answer] ")

        elif name == "tool_calls":
            console.print(f"\n[tool:start] {item.tool_name} input={item.input}", style="cyan")

            for delta in _safe_iter_projection(getattr(item, "output_deltas", None)):
                console.print(delta, end="", style="bright_black")

            if getattr(item, "error", None):
                console.print(f"\n[tool:error] {item.error}", style="bold red")
            else:
                console.print(f"\n[tool:done] {item.output}", style="green")

    console.print()


def main() -> None:
    setup_observability()

    from recipe_agent.agent import create_recipe_agent

    console = Console()
    agent = create_recipe_agent()

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        stream_answer(agent, question, console=console)
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

        stream_answer(agent, question, console=console)
