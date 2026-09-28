"""The 'R' in RAG: retrieve the CV excerpts most relevant to the user's question."""

import asyncio
import json
import math
import re
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

from rag.config import get_settings
from rag.llm import get_client

CV_DIR = Path("dataset")
INDEX_PATH = Path("rag/index.json")


class Chunk(BaseModel):
    """A piece of text from the CV, with its embedding vector (internal model — never sent to the frontend)."""

    source: str  # e.g. "experiences · Experience"
    text: str
    embedding: list[float] = Field(default_factory=list)


def _split_long(text: str, max_chars: int, overlap: int) -> list[str]:
    """Group paragraphs into chunks of at most max_chars, with overlap between chunks."""
    parts: list[str] = []
    current = ""
    for para in text.split("\n\n"):
        if current and len(current) + len(para) + 2 > max_chars:
            parts.append(current)
            current = current[-overlap:] + "\n\n" + para  # keep overlap between chunks
        else:
            current = f"{current}\n\n{para}" if current else para
    if current.strip():
        parts.append(current)
    return parts


def chunk_markdown(path: Path) -> list[Chunk]:
    """One '##' section = one chunk. Sections that are too long get re-split."""
    settings = get_settings()
    text = path.read_text(encoding="utf-8")

    chunks: list[Chunk] = []
    for section in re.split(r"\n(?=## )", text):
        if not section.strip():
            continue
        header = section.splitlines()[0].lstrip("# ").strip()
        source = f"{path.stem} · {header}" if header else path.stem
        for part in _split_long(section, settings.chunk_size, settings.chunk_overlap):
            chunks.append(Chunk(source=source, text=part.strip()))
    return chunks


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Request embedding vectors for N texts (single API call)."""
    response = await get_client().embeddings.create(
        model=get_settings().embedding_model,
        input=texts,
    )
    return [item.embedding for item in response.data]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Angle between two vectors: 1.0 = same direction, 0.0 = unrelated."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


@lru_cache
def load_index() -> tuple[Chunk, ...]:
    """Load the index once. Returns an empty tuple if the index hasn't been built yet."""
    if not INDEX_PATH.exists():
        print(f"⚠️ Index not found at {INDEX_PATH} — run 'python rag/retrieval.py' first")
        return ()
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return tuple(Chunk.model_validate(item) for item in data)


async def search(query: str, k: int | None = None) -> list[tuple[float, Chunk]]:
    """Return the k best chunks WITH their scores (0..1), best first."""
    settings = get_settings()
    (query_embedding,) = await embed_texts([query])

    scored = [
        (cosine_similarity(query_embedding, chunk.embedding), chunk)
        for chunk in load_index()
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[: (k or settings.top_k)]


def format_context(scored: list[tuple[float, Chunk]]) -> str:
    """Format scored chunks for injection into the system prompt."""
    return "\n---\n".join(f"[{c.source}]\n{c.text}" for _, c in scored)


async def build_context(query: str) -> str:
    """One-shot helper: search + format (used by scripts/tests)."""
    return format_context(await search(query))


if __name__ == "__main__":
    """Ingestion: CV -> chunks -> embeddings -> index.json. Re-run after every CV change."""

    async def ingest() -> None:
        if not CV_DIR.exists():
            raise SystemExit(f"Directory '{CV_DIR}/' not found — create it with your .md files")

        chunks: list[Chunk] = []
        for md_path in sorted(CV_DIR.glob("*.md")):
            file_chunks = chunk_markdown(md_path)
            print(f"  {md_path.name}: {len(file_chunks)} chunks")
            chunks.extend(file_chunks)
        print(f"{len(chunks)} chunks found, embedding...")

        embeddings = await embed_texts([c.text for c in chunks])
        for chunk, emb in zip(chunks, embeddings):
            chunk.embedding = emb

        INDEX_PATH.write_text(
            json.dumps([c.model_dump() for c in chunks]),
            encoding="utf-8",
        )
        print(f"✅ Index saved: {INDEX_PATH} ({INDEX_PATH.stat().st_size // 1024} KB)")

    asyncio.run(ingest())
