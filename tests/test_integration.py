"""Real API calls. Excluded by default (see addopts). Run explicitly:
    pytest -m integration
Requires: .env with valid keys + a built rag/index.json."""

import pytest

pytestmark = pytest.mark.integration


async def test_real_rewrite():
    from rag.providers.rewriter import rewrite_query
    corrected = await rewrite_query("parl de son projet")
    assert "projet" in corrected.lower()


async def test_real_search_returns_sorted_scores():
    from rag.retrieval import search
    scored = await search("What are your main skills?", k=3)
    assert len(scored) == 3
    scores = [s for s, _ in scored]
    assert scores == sorted(scores, reverse=True)
