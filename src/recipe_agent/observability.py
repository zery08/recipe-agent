from __future__ import annotations

import os

from dotenv import load_dotenv
from openinference.instrumentation.langchain import LangChainInstrumentor
from phoenix.otel import register

_PROJECT_NAME = "recipe-agent"


def setup_observability() -> None:
    """Configure Phoenix/OpenInference tracing when PHOENIX_ENDPOINT is set."""
    load_dotenv()

    endpoint = os.environ.get("PHOENIX_ENDPOINT")
    if not endpoint:
        return

    os.environ.setdefault("PHOENIX_COLLECTOR_ENDPOINT", endpoint)

    tracer_provider = register(
        endpoint=endpoint,
        project_name=os.environ.get("PHOENIX_PROJECT_NAME", _PROJECT_NAME),
        auto_instrument=False,
    )
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
