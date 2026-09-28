"""Groq provider — fallback LLM when Gemini is saturated (429/503)."""

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
    """One Groq client for the whole app."""
    settings = get_settings()
    return AsyncOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=settings.groq_api_key.get_secret_value(),
    )


async def stream_answer(
    question: str,
    history: list[ChatMessage] | None = None,
    context: str = "",
) -> AsyncGenerator[str, None]:
    """Stream Groq's answer, token by token.

    Universally-supported params only: NO reasoning_effort (Gemini-specific).
    """
    settings = get_settings()

    stream = await get_client().chat.completions.create(
        model=settings.groq_model,
        messages=build_messages(question, history or [], context),
        temperature=settings.temperature,
        max_tokens=4000,
        stream=True,
    )

    finish_reason = None
    async for chunk in stream:
        if chunk.choices:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
            if chunk.choices[0].finish_reason:
                finish_reason = chunk.choices[0].finish_reason

    logger.info("Groq stream end: finish_reason=%s", finish_reason)
