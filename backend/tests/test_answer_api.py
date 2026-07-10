"""API-level tests for /answer/ask."""

import pytest
from fastapi.testclient import TestClient

from app.models.retrieval import RetrievedChunk
from app.services import answer_service
from app.services.ollama_client import OllamaUnavailableError
from main import app
from tests.fakes import FakeOllamaClient

client = TestClient(app)


def _chunk(**overrides) -> RetrievedChunk:
    defaults = dict(
        chunk_id="chunk-1",
        document_id="doc-1",
        chunk_index=0,
        chunk_text="A data structure organizes data for efficient access.",
        page_number=1,
        similarity_score=0.8,
    )
    defaults.update(overrides)
    return RetrievedChunk(**defaults)


def test_ask_returns_grounded_answer(monkeypatch):
    fake_ollama = FakeOllamaClient(reply="Here is the grounded answer.")
    monkeypatch.setattr(answer_service, "ollama_client", fake_ollama)
    monkeypatch.setattr(
        answer_service, "retrieve_relevant_chunks", lambda **kwargs: [_chunk()]
    )

    response = client.post("/answer/ask", json={"query": "What is a data structure?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Here is the grounded answer."
    assert body["insufficient_context"] is False
    assert len(body["sources"]) == 1
    assert body["sources"][0]["page_number"] == 1


def test_ask_returns_insufficient_context_without_calling_ollama(monkeypatch):
    fake_ollama = FakeOllamaClient()
    monkeypatch.setattr(answer_service, "ollama_client", fake_ollama)
    monkeypatch.setattr(answer_service, "retrieve_relevant_chunks", lambda **kwargs: [])

    response = client.post("/answer/ask", json={"query": "Something not covered"})

    assert response.status_code == 200
    body = response.json()
    assert body["insufficient_context"] is True
    assert body["sources"] == []
    assert fake_ollama.last_call is None


def test_ask_returns_503_when_ollama_unavailable(monkeypatch):
    fake_ollama = FakeOllamaClient()
    fake_ollama.raise_on_chat = OllamaUnavailableError("Ollama is not running.")
    monkeypatch.setattr(answer_service, "ollama_client", fake_ollama)
    monkeypatch.setattr(
        answer_service, "retrieve_relevant_chunks", lambda **kwargs: [_chunk()]
    )

    response = client.post("/answer/ask", json={"query": "What is a data structure?"})

    assert response.status_code == 503
    assert "Ollama" in response.json()["detail"]


def test_ask_rejects_top_k_out_of_range():
    response = client.post("/answer/ask", json={"query": "x", "top_k": 0})
    assert response.status_code == 422
