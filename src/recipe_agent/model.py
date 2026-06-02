from __future__ import annotations

import os
import warnings
from typing import Any

from dotenv import load_dotenv
from langchain_core._api import LangChainBetaWarning
from langchain_core.messages import AIMessageChunk
from langchain_openai import ChatOpenAI

load_dotenv()
warnings.filterwarnings("ignore", category=LangChainBetaWarning)

# Environment variable convention: {ROLE}_{KEY}
# e.g. SUPERVISOR_MODEL, SUPERVISOR_API_KEY, TOOL_BASE_URL.
#
# TOOL_* falls back to SUPERVISOR_* when not set.
# SUPERVISOR_* falls back to built-in defaults.

_DEFAULTS = {
    "MODEL": "gpt-4o-mini",
    "BASE_URL": "https://api.openai.com/v1",
    "API_KEY": os.environ.get("OPENAI_API_KEY", ""),
}


def _get(prefix: str, key: str) -> str:
    value = os.environ.get(f"{prefix}_{key}")
    if value:
        return value
    if prefix != "SUPERVISOR":
        return os.environ.get(f"SUPERVISOR_{key}") or _DEFAULTS[key]
    return _DEFAULTS[key]


def _extract_text_from_reasoning_details(details: Any) -> str:
    if not isinstance(details, list):
        return ""

    parts: list[str] = []
    for detail in details:
        if not isinstance(detail, dict):
            continue
        for key in ("text", "summary", "reasoning", "content"):
            value = detail.get(key)
            if isinstance(value, str) and value:
                parts.append(value)
                break
    return "".join(parts)


def _extract_direct_reasoning_delta(delta: dict[str, Any]) -> str:
    for key in ("reasoning", "reasoning_content", "thinking"):
        value = delta.get(key)
        if isinstance(value, str) and value:
            return value
        if isinstance(value, dict):
            text = _extract_text_from_reasoning_details([value])
            if text:
                return text
    return ""


def _extract_reasoning_delta(raw_chunk: dict[str, Any]) -> str:
    choices = raw_chunk.get("choices") or raw_chunk.get("chunk", {}).get("choices") or []
    parts: list[str] = []

    for choice in choices:
        if not isinstance(choice, dict):
            continue

        delta = choice.get("delta") or choice.get("message") or {}
        if not isinstance(delta, dict):
            continue

        direct_text = _extract_direct_reasoning_delta(delta)
        if direct_text:
            parts.append(direct_text)
            continue

        parts.append(_extract_text_from_reasoning_details(delta.get("reasoning_details")))

    return "".join(parts)


class ReasoningChatOpenAI(ChatOpenAI):
    """ChatOpenAI variant that preserves OpenRouter-style reasoning chunks."""

    def _convert_chunk_to_generation_chunk(
        self,
        chunk: dict[str, Any],
        default_chunk_class: type,
        base_generation_info: dict | None,
    ):
        generation_chunk = super()._convert_chunk_to_generation_chunk(
            chunk,
            default_chunk_class,
            base_generation_info,
        )
        if generation_chunk is None:
            return None

        message = generation_chunk.message
        reasoning = _extract_reasoning_delta(chunk)
        if reasoning and isinstance(message, AIMessageChunk):
            message.additional_kwargs["reasoning"] = reasoning
            message.response_metadata.pop("model_provider", None)

        return generation_chunk


def build_model(prefix: str = "SUPERVISOR", **overrides: Any) -> ChatOpenAI:
    base_url = _get(prefix, "BASE_URL")
    model_kwargs: dict[str, Any] = {
        "model": _get(prefix, "MODEL"),
        "base_url": base_url,
        "api_key": _get(prefix, "API_KEY"),
        "temperature": 0.0,
        "streaming": True,
    }
    model_kwargs.update(overrides)

    if "openrouter.ai" in base_url:
        # OpenRouter-specific extension, not an OpenAI Chat Completions field.
        extra_body = dict(model_kwargs.get("extra_body") or {})
        reasoning = extra_body.get("reasoning")
        reasoning = dict(reasoning) if isinstance(reasoning, dict) else {}
        reasoning.setdefault("enabled", True)
        extra_body["reasoning"] = reasoning
        model_kwargs["extra_body"] = extra_body

    return ReasoningChatOpenAI(**model_kwargs)
