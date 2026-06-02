from __future__ import annotations

import os
import warnings
from typing import Any
from uuid import uuid4

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
        if not choices:
            return gen

        delta = choices[0].get("delta") or {}

        reasoning = delta.get("reasoning") or delta.get("reasoning_content") or ""

        if reasoning and isinstance(gen.message, AIMessageChunk):
            gen.message.additional_kwargs["reasoning"] = reasoning

        return gen

    def _stream_chat_model_events(
        self,
        messages,
        stop=None,
        run_manager=None,
        **kwargs,
    ):
        message_id = f"msg-{uuid4()}"

        yield {
            "event": "message-start",
            "id": message_id,
            "metadata": {
                "provider": "openai-compatible",
                "model": self.model_name,
            },
        }

        reasoning_full = ""
        text_full = ""
        saw_reasoning = False
        saw_text = False

        for gen in super()._stream(
            messages,
            stop=stop,
            run_manager=run_manager,
            **kwargs,
        ):
            msg = gen.message

            reasoning = msg.additional_kwargs.get("reasoning") or ""
            if reasoning:
                saw_reasoning = True
                reasoning_full += reasoning

                yield {
                    "event": "content-block-delta",
                    "index": 0,
                    "delta": {
                        "type": "reasoning-delta",
                        "reasoning": reasoning,
                    },
                }

            content = msg.content or ""
            if isinstance(content, str) and content:
                saw_text = True
                text_full += content

                yield {
                    "event": "content-block-delta",
                    "index": 1,
                    "delta": {
                        "type": "text-delta",
                        "text": content,
                    },
                }

        if saw_reasoning:
            yield {
                "event": "content-block-finish",
                "index": 0,
                "content": {
                    "type": "reasoning",
                    "reasoning": reasoning_full,
                },
            }

        if saw_text:
            yield {
                "event": "content-block-finish",
                "index": 1,
                "content": {
                    "type": "text",
                    "text": text_full,
                },
            }

        yield {
            "event": "message-finish",
        }


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
