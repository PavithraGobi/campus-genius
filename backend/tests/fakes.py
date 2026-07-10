"""Test doubles for the Supabase-backed stores and the embedding model.

Used to test document_service's orchestration logic (status transitions,
error handling) without needing real network access to Supabase or
Hugging Face — neither of which is reachable from this environment, and
neither of which should be hit by fast unit tests anyway.
"""

from datetime import datetime, timezone

from app.models.chunk import ChunkRecord
from app.models.document import DocumentRecord, DocumentStatus
from app.models.retrieval import RetrievedChunk


class FakeDocumentStore:
    def __init__(self) -> None:
        self.records: dict[str, DocumentRecord] = {}

    def create(self, record: DocumentRecord) -> DocumentRecord:
        self.records[record.id] = record
        return record

    def get(self, document_id: str) -> DocumentRecord | None:
        return self.records.get(document_id)

    def update_status(
        self,
        document_id: str,
        status: DocumentStatus,
        *,
        page_count: int | None = None,
        error_message: str | None = None,
    ) -> DocumentRecord | None:
        record = self.records.get(document_id)
        if record is None:
            return None
        record.status = status
        if page_count is not None:
            record.page_count = page_count
        record.error_message = error_message
        record.updated_at = datetime.now(timezone.utc)
        return record


class FakeChunkStore:
    def __init__(self) -> None:
        self.inserted: list[ChunkRecord] = []
        self.raise_on_insert: Exception | None = None
        self.search_results: list[RetrievedChunk] = []
        self.raise_on_search: Exception | None = None
        self.last_search_call: dict | None = None

    def insert_chunks(self, chunks: list[ChunkRecord]) -> None:
        if self.raise_on_insert:
            raise self.raise_on_insert
        self.inserted.extend(chunks)

    def search_similar(
        self,
        query_embedding: list[float],
        top_k: int,
        document_id: str | None = None,
    ) -> list[RetrievedChunk]:
        self.last_search_call = {
            "query_embedding": query_embedding,
            "top_k": top_k,
            "document_id": document_id,
        }
        if self.raise_on_search:
            raise self.raise_on_search
        return self.search_results[:top_k]


class FakeEmbeddingService:
    """Returns deterministic fixed-length vectors without loading any model."""

    def __init__(self, dim: int = 1024) -> None:
        self.dim = dim
        self.raise_on_embed: Exception | None = None

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if self.raise_on_embed:
            raise self.raise_on_embed
        return [[0.0] * self.dim for _ in texts]


class FakeOllamaClient:
    def __init__(self, reply: str = "This is a generated answer.") -> None:
        self.reply = reply
        self.raise_on_chat: Exception | None = None
        self.last_call: dict | None = None

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        self.last_call = {"system_prompt": system_prompt, "user_prompt": user_prompt}
        if self.raise_on_chat:
            raise self.raise_on_chat
        return self.reply
