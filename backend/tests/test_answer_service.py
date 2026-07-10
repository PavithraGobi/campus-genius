"""Tests for answer_service: grounded generation, insufficient-context
guard, and Ollama failure handling — using fakes throughout.
"""

import pytest

from app.models.retrieval import RetrievedChunk
from app.services import answer_service
from app.services.ollama_client import OllamaUnavailableError
from tests.fakes import FakeOllamaClient


def _chunk(**overrides) -> RetrievedChunk:
    defaults = dict(
        chunk_id="chunk-1",
        document_id="doc-1",
        chunk_index=0,
        chunk_text="A data structure is a way of organizing data.",
        page_number=3,
        similarity_score=0.8,
    )
    defaults.update(overrides)
    return RetrievedChunk(**defaults)


@pytest.fixture
def fake_ollama(monkeypatch):
    fake = FakeOllamaClient(reply="A data structure organizes data for efficient use.")
    monkeypatch.setattr(answer_service, "ollama_client", fake)
    return fake


def test_generates_grounded_answer_with_sufficient_context(monkeypatch, fake_ollama):
    chunks = [_chunk(similarity_score=0.8)]
    monkeypatch.setattr(
        answer_service, "retrieve_relevant_chunks", lambda **kwargs: chunks
    )

    result = answer_service.generate_answer("What is a data structure?")

    assert result.insufficient_context is False
    assert result.answer == "A data structure organizes data for efficient use."
    assert result.sources == chunks
    assert fake_ollama.last_call is not None


def test_no_chunks_skips_llm_and_returns_insufficient(monkeypatch, fake_ollama):
    monkeypatch.setattr(answer_service, "retrieve_relevant_chunks", lambda **kwargs: [])

    result = answer_service.generate_answer("Some obscure question")

    assert result.insufficient_context is True
    assert result.sources == []
    assert fake_ollama.last_call is None  # LLM must not be called


def test_low_similarity_skips_llm_and_returns_insufficient(monkeypatch, fake_ollama):
    weak_chunks = [_chunk(similarity_score=0.1)]
    monkeypatch.setattr(
        answer_service, "retrieve_relevant_chunks", lambda **kwargs: weak_chunks
    )

    result = answer_service.generate_answer("Unrelated question")

    assert result.insufficient_context is True
    assert result.sources == []
    assert fake_ollama.last_call is None


def test_prompt_includes_context_and_question(monkeypatch, fake_ollama):
    chunks = [_chunk(chunk_text="Arrays store elements in contiguous memory.", page_number=5)]
    monkeypatch.setattr(
        answer_service, "retrieve_relevant_chunks", lambda **kwargs: chunks
    )

    answer_service.generate_answer("What is an array?")

    user_prompt = fake_ollama.last_call["user_prompt"]
    assert "Arrays store elements in contiguous memory." in user_prompt
    assert "Page 5" in user_prompt
    assert "What is an array?" in user_prompt


def test_ollama_failure_propagates_as_ollama_unavailable_error(monkeypatch, fake_ollama):
    chunks = [_chunk(similarity_score=0.9)]
    monkeypatch.setattr(
        answer_service, "retrieve_relevant_chunks", lambda **kwargs: chunks
    )
    fake_ollama.raise_on_chat = OllamaUnavailableError("Ollama is not running.")

    with pytest.raises(OllamaUnavailableError):
        answer_service.generate_answer("What is a data structure?")


def test_document_id_and_top_k_forwarded_to_retrieval(monkeypatch, fake_ollama):
    captured = {}

    def fake_retrieve(**kwargs):
        captured.update(kwargs)
        return [_chunk(similarity_score=0.9)]

    monkeypatch.setattr(answer_service, "retrieve_relevant_chunks", fake_retrieve)

    answer_service.generate_answer("question", top_k=2, document_id="doc-42")

    assert captured["top_k"] == 2
    assert captured["document_id"] == "doc-42"
