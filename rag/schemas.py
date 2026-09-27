from typing import Literal
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)

class ChatRequest(BaseModel):
    messages: str = Field(min_length=1, max_length=1000)
    history: list[ChatMessage] = Field(default_factory=list, max_items=20)

class Source(BaseModel):
    title: str
    score: float = Field(ge=0, le=1)

class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)
