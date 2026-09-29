from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Routing & Server ---
    llm_provider: Literal["gemini", "groq"] = "gemini"
    allowed_origins: str = "http://127.0.0.1:5500,http://localhost:5500"

    # --- Shared LLM params (both providers) ---
    temperature: float = 0.3
    max_history: int = 5
    max_output_tokens: int = 4000

    # --- Gemini (primary) ---
    gemini_api_key: SecretStr
    llm_model: str = "gemini-3.8-flash"
    embedding_model: str = "gemini-embedding-2"
    reasoning_effort: str = "low"

    # --- Groq (fallback) ---
    groq_api_key: SecretStr | None = None
    groq_model: str = "openai/gpt-oss-120b"
    rewriter_model: str = "openai/gpt-oss-20b"


    # --- RAG ---
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
