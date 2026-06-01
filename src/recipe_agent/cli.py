from __future__ import annotations

import sys

from recipe_agent.agent import create_recipe_agent
from recipe_agent.streaming import stream_answer


def main() -> None:
    agent = create_recipe_agent()

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        stream_answer(agent, question)
        return

    print("Recipe Agent CLI. Type 'exit' to quit.")
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if question.lower() in {"exit", "quit", "q"}:
            return

        if not question:
            continue

        stream_answer(agent, question)
