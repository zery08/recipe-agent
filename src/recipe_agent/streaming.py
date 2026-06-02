from __future__ import annotations

from typing import Iterable

from rich.console import Console

_THINKING_STYLE = "dim yellow"
_TOOL_START_STYLE = "cyan"
_TOOL_DELTA_STYLE = "bright_black"
_TOOL_DONE_STYLE = "green"
_TOOL_ERROR_STYLE = "bold red"


def _safe_iter_projection(projection) -> Iterable[str]:
    if projection is None:
        return []
    return projection


def stream_answer(
    agent,
    question: str,
    *,
    console: Console | None = None,
    error_console: Console | None = None,
) -> None:
    console = console or Console()
    error_console = error_console or Console(stderr=True)

    payload = {"messages": [{"role": "user", "content": question}]}

    printed_thinking = False
    printed_answer = False

    stream = agent.stream_events(payload, version="v3")

    for name, item in stream.interleave("messages", "tool_calls"):
        if name == "messages":
            for thinking in _safe_iter_projection(getattr(item, "reasoning", None)):
                if not printed_thinking:
                    error_console.print(
                        "\n[thinking] ",
                        end="",
                        markup=False,
                        style=_THINKING_STYLE,
                    )
                    printed_thinking = True
                error_console.print(
                    thinking,
                    end="",
                    markup=False,
                    highlight=False,
                    style=_THINKING_STYLE,
                )

            for text in _safe_iter_projection(getattr(item, "text", None)):
                if not printed_answer:
                    console.print("\n[answer] ", end="", markup=False)
                    printed_answer = True
                console.print(text, end="", markup=False, highlight=False)

        elif name == "tool_calls":
            error_console.print(
                f"\n[tool:start] {item.tool_name} input={item.input}",
                markup=False,
                style=_TOOL_START_STYLE,
            )

            for delta in _safe_iter_projection(getattr(item, "output_deltas", None)):
                error_console.print(
                    delta,
                    end="",
                    markup=False,
                    highlight=False,
                    style=_TOOL_DELTA_STYLE,
                )

            if getattr(item, "error", None):
                error_console.print(
                    f"\n[tool:error] {item.error}",
                    markup=False,
                    style=_TOOL_ERROR_STYLE,
                )
            else:
                error_console.print(
                    f"\n[tool:done] {item.output}",
                    markup=False,
                    style=_TOOL_DONE_STYLE,
                )

    console.print()
