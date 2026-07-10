"""Retrieval result schema."""

from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    chunk_text: str
    page_number: int
    similarity_score: float
