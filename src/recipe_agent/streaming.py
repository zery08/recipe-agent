from __future__ import annotations

import sys
from typing import Iterable


def _safe_iter_projection(projection) -> Iterable[str]:
    if projection is None:
        return []
    return projection


def stream_answer(agent, question: str) -> None:
    payload = {"messages": [{"role": "user", "content": question}]}

    printed_thinking = False
    printed_answer = False

    stream = agent.stream_events(payload, version="v3")

    for name, item in stream.interleave("messages", "tool_calls"):
        if name == "messages":
            for thinking in _safe_iter_projection(getattr(item, "reasoning", None)):
                if not printed_thinking:
                    print("\n[thinking] ", end="", file=sys.stderr, flush=True)
                    printed_thinking = True
                print(thinking, end="", file=sys.stderr, flush=True)

            for text in _safe_iter_projection(getattr(item, "text", None)):
                if not printed_answer:
                    print("\n[answer] ", end="", flush=True)
                    printed_answer = True
                print(text, end="", flush=True)

        elif name == "tool_calls":
            print(
                f"\n[tool:start] {item.tool_name} input={item.input}",
                file=sys.stderr,
                flush=True,
            )

            for delta in _safe_iter_projection(getattr(item, "output_deltas", None)):
                print(delta, end="", file=sys.stderr, flush=True)

            if getattr(item, "error", None):
                print(f"\n[tool:error] {item.error}", file=sys.stderr, flush=True)
            else:
                print(f"\n[tool:done] {item.output}", file=sys.stderr, flush=True)

    print()
