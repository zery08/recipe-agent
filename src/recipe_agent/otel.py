from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator

from dotenv import load_dotenv

_REGISTERED = False
_ENABLED = False
_TRACER_PROVIDER: Any | None = None
_DEFAULT_ENDPOINT = "http://localhost:4317"
_DEFAULT_PROJECT_NAME = "recipe-agent"


def _is_enabled() -> bool:
    value = os.environ.get("PHOENIX_ENABLED", "true")
    return value.strip().lower() not in {"0", "false", "no", "off"}


def setup_otel() -> Any | None:
    """Register Phoenix OpenTelemetry tracing once for this process."""
    global _ENABLED, _REGISTERED, _TRACER_PROVIDER

    if _REGISTERED:
        return _TRACER_PROVIDER

    load_dotenv()
    _REGISTERED = True
    _ENABLED = _is_enabled()
    if not _ENABLED:
        return None

    try:
        from phoenix.otel import register
    except ImportError as exc:
        raise RuntimeError(
            "Phoenix tracing requires arize-phoenix-otel. Run `uv sync` "
            "after updating dependencies."
        ) from exc

    _TRACER_PROVIDER = register(
        endpoint=os.environ.get("PHOENIX_ENDPOINT", _DEFAULT_ENDPOINT),
        project_name=os.environ.get("PHOENIX_PROJECT_NAME", _DEFAULT_PROJECT_NAME),
        protocol="grpc",
        auto_instrument=True,
        batch=False,
        verbose=False,
    )
    return _TRACER_PROVIDER


@contextmanager
def phoenix_session(session_id: str | None) -> Iterator[None]:
    """Attach a Phoenix session id to spans created inside the context."""
    if not _REGISTERED:
        setup_otel()

    if not _ENABLED or not session_id:
        yield
        return

    from phoenix.otel import using_session

    with using_session(session_id):
        yield
