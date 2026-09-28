"""Data contracts shared across the app: API request, and SSE wire events."""

from typing import Literal

from pydantic import BaseModel, Field


# --- HTTP request contract (consumers: rag/llm.py, api/index.py) ---

class ChatMessage(BaseModel):
    """A message of the conversation, as exchanged with the frontend."""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    """Request sent by the portfolio chat widget."""

    message: str = Field(min_length=1, max_length=1000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


# --- Server-Sent Events: the wire format between API and the chat widget ---

class TokenEvent(BaseModel):
    """One streamed piece of the answer."""

    type: Literal["token"] = "token"
    content: str


class ErrorEvent(BaseModel):
    """Sent instead of tokens if the LLM call fails."""

    type: Literal["error"] = "error"
    message: str


class DoneEvent(BaseModel):
    """Sent last: the stream is over."""

    type: Literal["done"] = "done"


# --- Debug only: sent when ?debug=true, never shown to visitors ---

class Source(BaseModel):
    """A retrieved CV excerpt, with its similarity score."""

    title: str
    score: float = Field(ge=0.0, le=1.0)


class SourcesEvent(BaseModel):
    """The chunks used to ground the answer (developer testing only)."""

    type: Literal["sources"] = "sources"
    sources: list[Source]
