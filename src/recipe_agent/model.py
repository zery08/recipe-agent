from __future__ import annotations

import os
import warnings
from typing import Any

from dotenv import load_dotenv
from langchain_core._api import LangChainBetaWarning
from langchain_core.messages import AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk
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


class ReasoningChatOpenAI(ChatOpenAI):
    """
    GLM-4.7 등 delta['reasoning'] 필드를 반환하는 OpenAI-compatible 모델용 ChatOpenAI wrapper.

    LangChain ChatOpenAI가 기본적으로 보존하지 않는 reasoning chunk를
    AIMessageChunk.additional_kwargs['reasoning']에 넣어준다.
    """

    def _convert_chunk_to_generation_chunk(
        self,
        chunk: dict,
        default_chunk_class: type,
        base_generation_info: dict | None,
    ) -> ChatGenerationChunk | None:
        gen = super()._convert_chunk_to_generation_chunk(
            chunk,
            default_chunk_class,
            base_generation_info,
        )

        if gen is None:
            return None

        choices = chunk.get("choices") or chunk.get("chunk", {}).get("choices") or []

        if choices:
            delta = choices[0].get("delta") or {}
            reasoning = delta.get("reasoning") or ""

            if reasoning and isinstance(gen.message, AIMessageChunk):
                gen.message.additional_kwargs["reasoning"] = reasoning

        return gen


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
