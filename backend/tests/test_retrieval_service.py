"""Tests for retrieval_service — query embedding + similarity search
orchestration, using fakes for the embedding model and chunk store.
"""

import pytest

from app.models.retrieval import RetrievedChunk
from app.services import retrieval_service
from tests.fakes import FakeChunkStore, FakeEmbeddingService


@pytest.fixture
def fakes(monkeypatch):
    fake_chunks = FakeChunkStore()
    fake_embeddings = FakeEmbeddingService(dim=8)
    monkeypatch.setattr(retrieval_service, "chunk_store", fake_chunks)
    monkeypatch.setattr(retrieval_service, "embedding_service", fake_embeddings)
    return fake_chunks, fake_embeddings


def _sample_chunk(**overrides) -> RetrievedChunk:
    defaults = dict(
        chunk_id="chunk-1",
        document_id="doc-1",
        chunk_index=0,
        chunk_text="Some relevant text.",
        page_number=1,
        similarity_score=0.87,
    )
    defaults.update(overrides)
    return RetrievedChunk(**defaults)


def test_embeds_query_and_returns_search_results(fakes):
    fake_chunks, _ = fakes
    fake_chunks.search_results = [_sample_chunk()]

    results = retrieval_service.retrieve_relevant_chunks("What is a linked list?", top_k=3)

    assert len(results) == 1
    assert results[0].chunk_text == "Some relevant text."
    assert fake_chunks.last_search_call["top_k"] == 3
    assert fake_chunks.last_search_call["document_id"] is None
    assert len(fake_chunks.last_search_call["query_embedding"]) == 8


def test_passes_document_id_filter_through(fakes):
    fake_chunks, _ = fakes
    fake_chunks.search_results = [_sample_chunk()]

    retrieval_service.retrieve_relevant_chunks("query", top_k=5, document_id="doc-xyz")

    assert fake_chunks.last_search_call["document_id"] == "doc-xyz"


def test_results_ordered_by_similarity_are_preserved(fakes):
    fake_chunks, _ = fakes
    fake_chunks.search_results = [
        _sample_chunk(chunk_id="c1", similarity_score=0.95),
        _sample_chunk(chunk_id="c2", similarity_score=0.80),
        _sample_chunk(chunk_id="c3", similarity_score=0.60),
    ]

    results = retrieval_service.retrieve_relevant_chunks("query", top_k=3)

    assert [r.chunk_id for r in results] == ["c1", "c2", "c3"]


def test_empty_query_raises_value_error(fakes):
    with pytest.raises(ValueError):
        retrieval_service.retrieve_relevant_chunks("   ", top_k=3)


def test_invalid_top_k_raises_value_error(fakes):
    with pytest.raises(ValueError):
        retrieval_service.retrieve_relevant_chunks("query", top_k=0)


def test_uses_same_embedding_model_as_ingestion(fakes):
    """Sanity check: retrieval must go through the shared embedding_service
    singleton, not a separate model instance, so query and chunk vectors
    stay comparable."""
    fake_chunks, fake_embeddings = fakes
    fake_chunks.search_results = [_sample_chunk()]

    retrieval_service.retrieve_relevant_chunks("query", top_k=1)

    embedded_vector = fake_chunks.last_search_call["query_embedding"]
    assert embedded_vector == fake_embeddings.embed_texts(["anything"])[0]
