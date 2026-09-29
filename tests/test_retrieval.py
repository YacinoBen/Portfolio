from rag.retrieval import _split_long, chunk_markdown, cosine_similarity

# --- cosine similarity ---

def test_identical_vectors_score_one():
    assert cosine_similarity([1, 0], [1, 0]) == 1.0

def test_opposite_vectors_score_minus_one():
    assert cosine_similarity([1, 0], [-1, 0]) == -1.0

def test_unrelated_vectors_score_zero():
    assert cosine_similarity([1, 0], [0, 1]) == 0.0

def test_zero_vector_is_safe():
    # the guard `if norm_a and norm_b` — without it: ZeroDivisionError
    assert cosine_similarity([0, 0], [1, 1]) == 0.0


# --- chunking ---

def test_split_long_respects_limit_and_overlap():
    parts = _split_long("AAAA\n\nBBBB\n\nCCCC", max_chars=6, overlap=2)
    assert parts[0] == "AAAA"
    assert parts[1].startswith("AA\n\n")   # 2 chars carried over


def test_chunk_markdown_splits_on_h2(tmp_path):
    md = tmp_path / "cv.md"   # tmp_path: pytest gives a clean temp dir per test
    md.write_text("## Skills\nPython, C++\n\n## Projets\nCapture Moment",
                  encoding="utf-8")

    chunks = chunk_markdown(md)

    assert [c.source for c in chunks] == ["cv · Skills", "cv · Projets"]
    assert "Python, C++" in chunks[0].text
