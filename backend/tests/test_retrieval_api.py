"""API-level tests for /retrieval/search."""

import pytest
from fastapi.testclient import TestClient

from app.models.retrieval import RetrievedChunk
from app.services import retrieval_service
from main import app
from tests.fakes import FakeChunkStore, FakeEmbeddingService

client = TestClient(app)


@pytest.fixture(autouse=True)
def fakes(monkeypatch):
    fake_chunks = FakeChunkStore()
    fake_chunks.search_results = [
        RetrievedChunk(
            chunk_id="chunk-1",
            document_id="doc-1",
            chunk_index=0,
            chunk_text="Relevant passage about arrays.",
            page_number=2,
            similarity_score=0.91,
        )
    ]
    monkeypatch.setattr(retrieval_service, "chunk_store", fake_chunks)
    monkeypatch.setattr(retrieval_service, "embedding_service", FakeEmbeddingService(dim=8))
    return fake_chunks


def test_search_returns_ranked_chunks():
    response = client.post("/retrieval/search", json={"query": "What is an array?"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["chunk_text"] == "Relevant passage about arrays."
    assert body[0]["page_number"] == 2
    assert body[0]["similarity_score"] == 0.91


def test_search_accepts_top_k_and_document_id(fakes):
    response = client.post(
        "/retrieval/search",
        json={"query": "arrays", "top_k": 2, "document_id": "doc-42"},
    )

    assert response.status_code == 200
    assert fakes.last_search_call["top_k"] == 2
    assert fakes.last_search_call["document_id"] == "doc-42"


def test_search_rejects_empty_query():
    response = client.post("/retrieval/search", json={"query": "   "})
    assert response.status_code == 400


def test_search_rejects_top_k_out_of_range():
    response = client.post("/retrieval/search", json={"query": "arrays", "top_k": 0})
    assert response.status_code == 422  # pydantic Field(ge=1) validation

    response2 = client.post("/retrieval/search", json={"query": "arrays", "top_k": 500})
    assert response2.status_code == 422  # pydantic Field(le=50) validation
