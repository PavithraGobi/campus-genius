"""Chunk schema — mirrors the `chunks` table from the Supabase migration."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ChunkDraft(BaseModel):
    """A chunk before embedding — output of the chunking step."""

    chunk_index: int
    page_number: int
    chunk_text: str


class ChunkRecord(BaseModel):
    """A chunk ready to persist — includes its embedding."""

    id: str | None = None
    document_id: str
    chunk_index: int
    chunk_text: str
    embedding: list[float]
    page_number: int
    token_count: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
