from __future__ import annotations

import sys
import uuid
from typing import Iterable

from rich.console import Console
from rich.text import Text

from recipe_agent.otel import phoenix_session, setup_otel

console = Console()


def _safe_iter_projection(projection) -> Iterable[str]:
    if projection is None:
        return []
    return projection


def _print_chunk(
    target: Console,
    text: str,
    *,
    style: str | None = None,
    end: str = "",
) -> None:
    target.print(
        Text(str(text), style=style),
        end=end,
        highlight=False,
        soft_wrap=True,
    )
    target.file.flush()


def _event_delta(event: object, *keys: str) -> str:
    if not isinstance(event, dict):
        return ""

    delta = event.get("delta")
    if not isinstance(delta, dict):
        return ""

    for key in keys:
        value = delta.get(key)
        if isinstance(value, str):
            return value

    return ""


def stream_answer(agent, question: str, *, session_id: str | None = None) -> None:
    payload = {"messages": [{"role": "user", "content": question}]}

    printed_thinking = False
    printed_answer = False

    with phoenix_session(session_id):
        stream = agent.stream_events(payload, version="v3")

        for name, item in stream.interleave("messages", "tool_calls"):
            if name == "messages":
                for event in item:
                    thinking = _event_delta(event, "reasoning", "reasoning_content")
                    text = _event_delta(event, "text", "content")

                    if thinking:
                        if not printed_thinking:
                            _print_chunk(console, "\n[thinking] ", style="dim")
                            printed_thinking = True
                        _print_chunk(console, thinking, style="dim")

                    if text:
                        if not printed_answer:
                            _print_chunk(console, "\n[answer] ")
                            printed_answer = True
                        _print_chunk(console, text)

            elif name == "tool_calls":
                console.print(
                    Text(
                        f"\n[tool:start] {item.tool_name} input={item.input}",
                        style="cyan",
                    )
                )

                for delta in _safe_iter_projection(getattr(item, "output_deltas", None)):
                    _print_chunk(console, str(delta), style="cyan")

                if getattr(item, "error", None):
                    console.print(Text(f"\n[tool:error] {item.error}", style="red"))
                else:
                    console.print(Text(f"\n[tool:done] {item.output}", style="cyan"))

    console.print()


def main() -> None:
    setup_otel()

    from recipe_agent.agent import create_recipe_agent

    agent = create_recipe_agent()
    session_id = str(uuid.uuid4())

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        stream_answer(agent, question, session_id=session_id)
        return

    console.print("Recipe Agent CLI. Type 'exit' to quit.", style="bold")
    while True:
        try:
            question = console.input("\n[bold cyan]> [/]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            return

        if question.lower() in {"exit", "quit", "q"}:
            return

        if not question:
            continue

        stream_answer(agent, question, session_id=session_id)
