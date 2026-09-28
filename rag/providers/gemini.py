"""Gemini provider — primary LLM. Raises on errors; fallback is NOT its job."""

import logging
from collections.abc import AsyncGenerator
from functools import lru_cache

from openai import AsyncOpenAI

from rag.config import get_settings
from rag.providers.prompt import build_messages
from rag.schemas import ChatMessage

logger = logging.getLogger("uvicorn.error")


@lru_cache
def get_client() -> AsyncOpenAI:
    """One Gemini client for the whole app (connection pool reused)."""
    settings = get_settings()
    return AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=settings.gemini_api_key.get_secret_value(),
    )


async def stream_answer(
    question: str,
    history: list[ChatMessage] | None = None,
    context: str = "",
) -> AsyncGenerator[str, None]:
    """Stream Gemini's answer, token by token.

    Provider-specific params here: reasoning_effort (thinking control),
    which Groq/Llama does not know. Errors propagate to the caller.
    """
    settings = get_settings()

    stream = await get_client().chat.completions.create(
        model=settings.llm_model,
        messages=build_messages(question, history or [], context),
        temperature=settings.temperature,
        max_tokens=4000,  # INCLUDES reasoning tokens (~1024 for "low")
        reasoning_effort=settings.reasoning_effort,
        stream=True,
    )

    finish_reason = None
    async for chunk in stream:
        if chunk.choices:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
            if chunk.choices[0].finish_reason:
                finish_reason = chunk.choices[0].finish_reason

    logger.info("Gemini stream end: finish_reason=%s", finish_reason)
