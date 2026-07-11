"""Chunk persistence — Supabase-backed."""

from app.core.supabase_client import get_supabase_client
from app.models.chunk import ChunkRecord
from app.models.retrieval import RetrievedChunk

TABLE = "chunks"
MATCH_FUNCTION = "match_chunks"


class ChunkStore:
    def insert_chunks(self, chunks: list[ChunkRecord]) -> None:
        if not chunks:
            return

        client = get_supabase_client()
        payload = [
            {
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "chunk_text": chunk.chunk_text,
                "embedding": chunk.embedding,
                "page_number": chunk.page_number,
                "token_count": chunk.token_count,
            }
            for chunk in chunks
        ]
        client.table(TABLE).insert(payload).execute()

    def search_similar(
        self,
        query_embedding: list[float],
        top_k: int,
        document_id: str | None = None,
    ) -> list[RetrievedChunk]:
        """Vector similarity search via the match_chunks Postgres function
        (see db/migrations/002_match_chunks_function.sql).
        """
        client = get_supabase_client()
        params = {
            "query_embedding": query_embedding,
            "match_count": top_k,
            "filter_document_id": document_id,
        }
        response = client.rpc(MATCH_FUNCTION, params).execute()

        return [
            RetrievedChunk(
                chunk_id=row["id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                chunk_text=row["chunk_text"],
                page_number=row["page_number"],
                similarity_score=row["similarity"],
            )
            for row in response.data
        ]

    def get_ordered_chunks(
        self, document_id: str, limit: int | None = None
    ) -> list[RetrievedChunk]:
        """Return a document's chunks in document order (by chunk_index).

        Unlike `search_similar`, this isn't a similarity search — there's no
        query to search against. Viva question generation needs broad
        coverage across a document rather than chunks relevant to a specific
        question, so it pulls chunks in reading order instead.

        `similarity_score` is set to 1.0 on the returned chunks since it's
        not a meaningful value here; it's kept only so this can reuse the
        existing RetrievedChunk shape.
        """
        client = get_supabase_client()
        query = (
            client.table(TABLE)
            .select("id, document_id, chunk_index, chunk_text, page_number")
            .eq("document_id", document_id)
            .order("chunk_index")
        )
        if limit is not None:
            query = query.limit(limit)
        response = query.execute()

        return [
            RetrievedChunk(
                chunk_id=row["id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                chunk_text=row["chunk_text"],
                page_number=row["page_number"],
                similarity_score=1.0,
            )
            for row in response.data
        ]


chunk_store = ChunkStore()
