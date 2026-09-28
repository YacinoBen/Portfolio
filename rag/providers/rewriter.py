"""Query rewriting — fix typos/grammar BEFORE retrieval and generation.

This is the pipeline's input gate: the corrected query is validated by
Pydantic BEFORE being used. On any failure we return the original
question (fail-open: the chat must never block because of the rewriter).
"""

import logging

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from rag.config import get_settings

logger = logging.getLogger("uvicorn.error")

REWRITE_PROMPT = """\
You are a query corrector for a portfolio chatbot.
Rewrite the user's message: fix typos, spelling, grammar and punctuation.
Make it a clear, well-formed question or request.
Do NOT answer it. Do NOT change its meaning or its language.
Reply ONLY with JSON: {"query": "..."}"""


class RewrittenQuery(BaseModel):
    """Contract the rewriter LLM must fill — validated BEFORE use."""

    query: str = Field(min_length=1, max_length=1000)


async def rewrite_query(question: str) -> str:
    """Return the corrected question, or the original on any failure."""
    settings = get_settings()
    try:
        client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.groq_api_key.get_secret_value(),
        )
        response = await client.chat.completions.create(
            model=settings.rewriter_model,
            messages=[
                {"role": "system", "content": REWRITE_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0.0,
            max_tokens=200,
            response_format={"type": "json_object"},  # force valid JSON
        )
        raw = response.choices[0].message.content
        corrected = RewrittenQuery.model_validate_json(raw).query

        if corrected != question:
            logger.info("Query rewritten: %r -> %r", question[:60], corrected[:60])
        return corrected

    except Exception as exc:
        # Fail-open: a broken rewriter must degrade to "no correction",
        # exactly like before this feature existed. Never block the chat.
        logger.warning("Query rewrite failed (%s) — using original", exc)
        return question
