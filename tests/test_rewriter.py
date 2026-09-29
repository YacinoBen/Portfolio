from types import SimpleNamespace
from unittest.mock import AsyncMock

from rag.providers import rewriter


def _fake_client(content: str):
    """A stand-in AsyncOpenAI client returning a canned completion."""
    completion = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )
    return SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=AsyncMock(return_value=completion)))
    )


async def test_rewrite_success(monkeypatch):
    monkeypatch.setattr(rewriter, "AsyncOpenAI",
                        lambda **kw: _fake_client('{"query": "Parle-moi de son projet."}'))
    assert await rewriter.rewrite_query("parl de son projet") == "Parle-moi de son projet."


async def test_fail_open_on_invalid_json(monkeypatch):
    monkeypatch.setattr(rewriter, "AsyncOpenAI",
                        lambda **kw: _fake_client("this is not json"))
    # ValidationError -> caught -> original question returned
    assert await rewriter.rewrite_query("parl de son projet") == "parl de son projet"


async def test_fail_open_on_provider_crash(monkeypatch):
    def boom(**kw):
        raise RuntimeError("API down")
    monkeypatch.setattr(rewriter, "AsyncOpenAI", boom)
    assert await rewriter.rewrite_query("parl de son projet") == "parl de son projet"
