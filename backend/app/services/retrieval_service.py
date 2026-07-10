"""Query retrieval.

Embeds a user's question with the same model used at ingestion time
(BAAI/bge-m3, via embedding_service) and searches for similar chunks in
Supabase. Deliberately has no knowledge of Ollama or answer generation —
that's Phase 6, built on top of this.
"""

from app.models.retrieval import RetrievedChunk
from app.services.chunk_store import chunk_store
from app.services.embedding_service import embedding_service


def retrieve_relevant_chunks(
    query: str,
    top_k: int = 5,
    document_id: str | None = None,
) -> list[RetrievedChunk]:
    """Return the top-k chunks most similar to the query.

    Raises ValueError for an empty/whitespace-only query rather than
    silently embedding nothing.
    """
    query = query.strip()
    if not query:
        raise ValueError("Query must not be empty.")
    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    query_embedding = embedding_service.embed_texts([query])[0]
    return chunk_store.search_similar(query_embedding, top_k, document_id)
