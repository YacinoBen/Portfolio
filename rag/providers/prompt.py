"""Shared prompt building — used by every provider, depends on nothing else."""

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


def build_messages(
    question: str,
    history: list[ChatMessage],
    context: str = "",
) -> list[dict]:
    """Assemble the full conversation: system prompt + trimmed history + question.

    Shared by all providers: the SAME conversation is sent whichever
    model answers — only the transport differs.
    """
    settings = get_settings()

    system = SYSTEM_PROMPT
    if context:
        system += f"\n\nReliable CV excerpts:\n{context}"

    messages: list[dict] = [{"role": "system", "content": system}]
    messages += [msg.model_dump() for msg in history[-settings.max_history:]]
    messages.append({"role": "user", "content": question})
    return messages
