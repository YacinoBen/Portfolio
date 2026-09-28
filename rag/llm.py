import asyncio
from collections.abc import AsyncGenerator
from functools import lru_cache

from openai import AsyncOpenAI

from rag.config import get_settings
from rag.schemas import ChatMessage

SYSTEM_PROMPT = """\
You are the virtual assistant for Yacine Benaffane's portfolio.

Your role is to present Yacine Benaffane's background, skills, and projects to visitors and recruiters.

Your pririority is to talk about Yacine's C++ skills and SOLID principles Design Patterns Software Engineering, as they are the most relevant to his career. You can also mention his Python and LLM experience, but only as secondary information.

Imperative rules:
- Speak about Yacine in the third person (e.g., "Yacine worked on...", "His skills include..."). NEVER answer using "I" or "me" to refer to him.
- Answer in the language used by the visitor.
- Stay strictly focused on the information provided in Yacine's resume and portfolio; politely decline any off-topic questions.
- Keep answers concise (3 to 6 sentences), maintaining a professional and friendly tone.
- If the requested information is not available in the context or resume, state it clearly: NEVER fabricate information.
"""

@lru_cache
def get_client() -> AsyncOpenAI:

    settings = get_settings()
    return AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=settings.gemini_api_key.get_secret_value(),
    )


def build_messages(
    question: str,
    history: list[ChatMessage],
    context: str = "",
) -> list[dict]:
    settings = get_settings()

    system = SYSTEM_PROMPT
    if context:
        system += f"\n\nReliable excerpts from the CV :\n{context}"

    messages: list[dict] = [{"role": "system", "content": system}]
    messages += [msg.model_dump() for msg in history[-settings.max_history:]]
    messages.append({"role": "user", "content": question})
    return messages


async def stream_answer(
    question: str,
    history: list[ChatMessage] | None = None,
    context: str = "",
) -> AsyncGenerator[str, None]:
    """Ask a question to the LLM and stream the answer as it is generated."""
    history = history or []

    stream = await get_client().chat.completions.create(
        model=get_settings().llm_model,
        max_tokens=1000,
        messages=build_messages(question, history, context),
        temperature=get_settings().temperature,
        stream=True,
    )

    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
