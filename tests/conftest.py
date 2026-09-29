"""Shared setup for every test."""

import pytest

from rag.config import get_settings
from rag.retrieval import load_index


@pytest.fixture(autouse=True)
def _fresh_caches():
    """lru_cache persists ACROSS tests — without this reset, one test's
    configuration or index leaks into the next (exactly the same lesson
    as 'restart uvicorn after rebuilding the index')."""
    get_settings.cache_clear()
    load_index.cache_clear()
    yield
    get_settings.cache_clear()
    load_index.cache_clear()
