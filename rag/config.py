from functools import lru_cache 
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: SecretStr

    llm_model: str = "gemini-2.5-flash"
    embedding_model: str = "gemini-embedding-2"

    # RAG settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5
    temperature: float = 0.3
    max_history: int = 5

@lru_cache
def get_settings() -> Settings:
    return Settings()
