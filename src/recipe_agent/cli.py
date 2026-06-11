from __future__ import annotations

import sys
import uuid
from typing import Iterable

from rich.console import Console
from rich.text import Text

from recipe_agent.otel import phoenix_session, setup_otel

console = Console()
_MAX_HISTORY_MESSAGES = 12

ChatMessage = dict[str, str]


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


def _trim_history(history: list[ChatMessage]) -> list[ChatMessage]:
    return history[-_MAX_HISTORY_MESSAGES:]


_SUBAGENT_TOOL_NAME = "task"


def _stream_message_item(
    item,
    state: dict[str, bool],
    *,
    prefix: str = "",
    text_style: str | None = None,
    answer_chunks: list[str] | None = None,
) -> None:
    for event in item:
        thinking = _event_delta(event, "reasoning", "reasoning_content")
        text = _event_delta(event, "text", "content")

        if thinking:
            if not state["thinking"]:
                _print_chunk(console, f"\n{prefix}[thinking] ", style="dim")
                state["thinking"] = True
            _print_chunk(console, thinking, style="dim")

        if text:
            if not state["answer"]:
                _print_chunk(console, f"\n{prefix}[answer] ", style=text_style)
                state["answer"] = True
            if answer_chunks is not None:
                answer_chunks.append(text)
            _print_chunk(console, text, style=text_style)


def _stream_tool_call(item, *, style: str = "cyan") -> None:
    console.print(
        Text(
            f"\n[tool:start] {item.tool_name} input={item.input}",
            style=style,
        )
    )

    for delta in _safe_iter_projection(getattr(item, "output_deltas", None)):
        _print_chunk(console, str(delta), style=style)

    if getattr(item, "error", None):
        console.print(Text(f"\n[tool:error] {item.error}", style="red"))
    else:
        console.print(Text(f"\n[tool:done] {item.output}", style=style))


def _stream_subagent(handle, label: str) -> None:
    """Stream a subagent's messages and tool calls live from its subgraph handle.

    Iterating the handle's projections drives the shared root pump, so
    tokens print as the subagent produces them.
    """
    prefix = f"[{label}] "
    state = {"thinking": False, "answer": False}

    for name, item in handle.interleave("messages", "tool_calls"):
        if name == "messages":
            _stream_message_item(item, state, prefix=prefix, text_style="green")
        elif name == "tool_calls":
            _stream_tool_call(item, style="green")

    if getattr(handle, "error", None):
        console.print(Text(f"\n{prefix}failed: {handle.error}", style="red"))
    else:
        console.print(Text(f"\n{prefix}{handle.status}", style="green"))


def stream_answer(
    agent,
    question: str,
    *,
    session_id: str | None = None,
    history: list[ChatMessage] | None = None,
) -> str:
    messages = [
        *_trim_history(history or []),
        {"role": "user", "content": question},
    ]
    payload = {"messages": messages}

    state = {"thinking": False, "answer": False}
    answer_chunks: list[str] = []
    pending_subagents: list[str] = []

    with phoenix_session(session_id):
        stream = agent.stream_events(payload, version="v3")

        for name, item in stream.interleave("messages", "tool_calls", "subgraphs"):
            if name == "messages":
                _stream_message_item(item, state, answer_chunks=answer_chunks)

            elif name == "tool_calls":
                if item.tool_name == _SUBAGENT_TOOL_NAME:
                    # The subagent runs as a nested subgraph; its tokens
                    # arrive via the matching "subgraphs" handle. Draining
                    # output_deltas here would pump the whole subagent run
                    # to completion before the handle is consumed.
                    subagent_type = (item.input or {}).get(
                        "subagent_type", "subagent"
                    )
                    pending_subagents.append(subagent_type)
                    console.print(
                        Text(
                            f"\n[subagent:start] {subagent_type} "
                            f"input={item.input}",
                            style="green",
                        )
                    )
                else:
                    _stream_tool_call(item)

            elif name == "subgraphs":
                label = (
                    pending_subagents.pop(0)
                    if pending_subagents
                    else (item.graph_name or "subagent")
                )
                _stream_subagent(item, label)

    console.print()
    return "".join(answer_chunks).strip()


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
    history: list[ChatMessage] = []
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

        answer = stream_answer(
            agent,
            question,
            session_id=session_id,
            history=history,
        )
        history.append({"role": "user", "content": question})
        if answer:
            history.append({"role": "assistant", "content": answer})
        history = _trim_history(history)
