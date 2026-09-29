from rag.config import get_settings
from rag.providers.prompt import build_messages
from rag.schemas import ChatMessage


def test_system_first_and_user_last():
    msgs = build_messages("hi", [], "CV CONTEXT")
    assert msgs[0]["role"] == "system"
    assert "CV CONTEXT" in msgs[0]["content"]     # context injected
    assert msgs[-1] == {"role": "user", "content": "hi"}


def test_history_trimmed_to_max_history():
    limit = get_settings().max_history
    history = [ChatMessage(role="user", content=f"msg {i}") for i in range(limit + 4)]

    msgs = build_messages("hi", history)

    assert len(msgs) == 2 + limit                 # system + trimmed + question
    assert msgs[1]["content"] == f"msg {4}"       # oldest messages dropped
