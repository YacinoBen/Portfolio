"""FastAPI application: wires schemas + retrieval + llm into an HTTP API.

File location matters: Vercel auto-detects `api/index.py` as a serverless function.
"""

import logging
from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import RateLimitError
from pydantic import BaseModel

from rag.config import get_settings
from rag.llm import stream_answer
from rag.providers.rewriter import rewrite_query
from rag.retrieval import format_context, search
from rag.schemas import (
    ChatRequest,
    DoneEvent,
    ErrorEvent,
    Source,
    SourcesEvent,
    TokenEvent,
)

logger = logging.getLogger("uvicorn.error")
settings = get_settings()

app = FastAPI(
    title="Portfolio RAG API",
    version="0.1.0",
    description="Chat with my CV — RAG with embeddings + LLM, streamed as SSE.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.allowed_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _sse(event: BaseModel) -> str:
    """Format one Pydantic event as an SSE frame: 'data: {json}\\n\\n'."""
    return f"data: {event.model_dump_json()}\n\n"


@app.get("/api/health")
async def health() -> dict[str, str]:
    """Liveness probe — the simplest possible FastAPI route."""
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(request: ChatRequest, debug: bool = False) -> StreamingResponse:
    """Full RAG pipeline: rewrite -> retrieve -> stream (Server-Sent Events)."""

    # 0. Input gate: fix typos/grammar BEFORE retrieval and generation.
    #    The visitor still sees THEIR message in the UI; only the pipeline
    #    works with the corrected version.
    question = await rewrite_query(request.message)

    # 1. Retrieval: find the CV chunks most relevant to the corrected question.
    try:
        scored = await search(question)
    except Exception as exc:
        # Error BEFORE streaming: headers not sent yet, a proper HTTP
        # error status is still possible.
        raise HTTPException(status_code=503, detail="Retrieval unavailable") from exc

    # 2. Telemetry: for the developer's logs, never shown to visitors.
    #    Both versions logged so you can SEE what the rewriter changed.
    logger.info(
        "retrieval %r (asked: %r) -> %s",
        question[:60],
        request.message[:60],
        [(c.source, round(score, 2)) for score, c in scored],
    )

    # 3. Build the context injected into the system prompt.
    context = format_context(scored)

    # 4. Stream the answer as typed SSE events.
    async def event_stream() -> AsyncGenerator[str, None]:
        # Debug mode only (?debug=true): let the developer see what was retrieved.
        if debug:
            yield _sse(SourcesEvent(sources=[
                Source(title=c.source, score=round(score, 3))
                for score, c in scored
            ]))

        try:
            async for token in stream_answer(question, request.history, context):
                yield _sse(TokenEvent(content=token))
        except RateLimitError:
            yield _sse(ErrorEvent(message="Rate limit reached — please retry in a minute."))
        except Exception:
            logger.exception("LLM call failed")  # full traceback in server logs
            yield _sse(ErrorEvent(message="The assistant is unavailable — please try again in a moment."))

    return StreamingResponse(event_stream(), media_type="text/event-stream")
