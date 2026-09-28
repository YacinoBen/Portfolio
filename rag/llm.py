"""Facade — the ONLY public entry point for LLM calls.

api/index.py imports stream_answer from here and does not know which
provider answered. Provider selection and fallback live in this file.
"""

import logging
from collections.abc import AsyncGenerator

from openai import InternalServerError, RateLimitError

from rag.config import get_settings
from rag.providers import gemini, groq
from rag.schemas import ChatMessage

logger = logging.getLogger("uvicorn.error")

# Fail fast: refuse to start with an impossible provider configuration.
_settings = get_settings()
if _settings.llm_provider == "groq" and _settings.groq_api_key is None:
    raise RuntimeError("LLM_PROVIDER=groq but GROQ_API_KEY is missing in .env")

async def stream_answer(
    question: str,
    history: list[ChatMessage] | None = None,
    context: str = "",
) -> AsyncGenerator[str, None]:
    settings = get_settings()

    # Provider selection: config decides the primary, the other one is the fallback.
    primary = gemini if settings.llm_provider == "gemini" else groq
    fallback = groq if primary is gemini else gemini

    try:
        first_token, stream = await _open_stream(primary, question, history, context)
    except (RateLimitError, InternalServerError) as exc:
        logger.warning("%s unavailable (%s) — falling back",
                       primary.__name__, exc)
        first_token, stream = await _open_stream(fallback, question, history, context)

    if first_token is not None:
        yield first_token
    async for token in stream:
        yield token


async def _open_stream(provider, question, history, context):
    """Open the stream NOW and return (first_token, rest_of_stream).

    Forcing the first __anext__() is what makes provider errors (429,
    503...) surface HERE — inside the facade's try/except — instead of
    during the later, unprotected iteration. The first token is buffered
    and re-yielded so nothing is lost.
    """
    agen = provider.stream_answer(question, history, context)
    try:
        first_token = await agen.__anext__()
    except StopAsyncIteration:
        return None, agen  # empty stream (no error, no content)
    return first_token, agen
