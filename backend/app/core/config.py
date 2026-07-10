"""
Application configuration.

Loads settings from environment variables (and a local .env file, if present).
Keep this file the single source of truth for config — other modules should
import `settings` from here rather than reading os.environ directly.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_name: str = "Campus Genius API"
    app_env: str = "development"

    # CORS - comma-separated origins in .env, parsed into a list below
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Supabase (used in later phases)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # Ollama (used in later phases)
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:7b-instruct"

    # Embeddings (used in later phases)
    embedding_model: str = "BAAI/bge-m3"

    # PDF ingestion
    upload_dir: str = "storage/uploads"
    max_upload_size_mb: int = 20

    # Chunking
    chunk_size_words: int = 200
    chunk_overlap_words: int = 30

    # Retrieval
    retrieval_default_top_k: int = 5

    # Answer generation
    ollama_timeout_seconds: int = 120
    # Below this similarity score, context is treated as insufficient and
    # the LLM is not called at all — a deterministic guard against
    # hallucinating from weak/irrelevant matches. Heuristic default; revisit
    # during Phase 9 evaluation once real query/document pairs exist.
    min_similarity_threshold: float = 0.35

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — avoids re-parsing the environment on every import."""
    return Settings()


settings = get_settings()
