import pytest
from pydantic import ValidationError

from rag.config import Settings


def test_missing_gemini_key_fails_fast(monkeypatch):
    """Reproduces the exact Vercel incident: no env vars, no .env -> crash
    at startup with a clear message, not a mysterious 500 in production."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValidationError, match="gemini_api_key"):
        Settings(_env_file=None)   # _env_file=None: ignore the local .env
