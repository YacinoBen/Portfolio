from fastapi.testclient import TestClient

from api.index import app
from rag.retrieval import Chunk

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_empty_message_is_422():
    # Pydantic validation, before ANY of our code runs
    assert client.post("/api/chat", json={"message": ""}).status_code == 422


def test_chat_streams_sse(monkeypatch):
    async def fake_rewrite(q): return q
    async def fake_search(q, k=None):
        return [(0.9, Chunk(source="test · topic", text="body", embedding=[]))]
    async def fake_stream(q, history=None, context=""):
        yield "Hello"
        yield " world"

    monkeypatch.setattr("api.index.rewrite_query", fake_rewrite)
    monkeypatch.setattr("api.index.search", fake_search)
    monkeypatch.setattr("api.index.stream_answer", fake_stream)

    with client.stream("POST", "/api/chat", json={"message": "hi"}) as r:
        body = "".join(r.iter_text())

    assert '{"type":"token","content":"Hello"}' in body
    assert '{"type":"done"}' in body
