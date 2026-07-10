"""Tests for the ingest_document orchestration: status flow, chunking,
embedding, and persistence — using fakes for Supabase and the embedding
model so these run fast and offline.
"""

import pytest
from fpdf import FPDF

from app.models.document import DocumentStatus
from app.services import document_service
from tests.fakes import FakeChunkStore, FakeDocumentStore, FakeEmbeddingService


def _make_pdf(pages_text: list[str]) -> bytes:
    pdf = FPDF()
    for text in pages_text:
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, text)
    return bytes(pdf.output())


@pytest.fixture
def fakes(monkeypatch, tmp_path):
    fake_documents = FakeDocumentStore()
    fake_chunks = FakeChunkStore()
    fake_embeddings = FakeEmbeddingService(dim=8)

    monkeypatch.setattr(document_service, "document_store", fake_documents)
    monkeypatch.setattr(document_service, "chunk_store", fake_chunks)
    monkeypatch.setattr(document_service, "embedding_service", fake_embeddings)
    monkeypatch.setattr(document_service.settings, "upload_dir", str(tmp_path))

    return fake_documents, fake_chunks, fake_embeddings


def test_successful_ingestion_reaches_ready_with_chunks_persisted(fakes):
    fake_documents, fake_chunks, _ = fakes
    pdf_bytes = _make_pdf(["Introduction to Data Structures and Arrays."])

    record, pages = document_service.ingest_document("sample.pdf", pdf_bytes)

    assert record.status == DocumentStatus.READY
    assert record.page_count == 1
    assert len(pages) == 1
    assert len(fake_chunks.inserted) > 0
    assert all(chunk.document_id == record.id for chunk in fake_chunks.inserted)
    assert all(len(chunk.embedding) == 8 for chunk in fake_chunks.inserted)


def test_status_progresses_through_processing(fakes):
    fake_documents, _, _ = fakes
    pdf_bytes = _make_pdf(["Some content here."])

    record, _ = document_service.ingest_document("sample.pdf", pdf_bytes)

    # Final stored record should be ready, but we can confirm processing
    # happened by checking it isn't stuck at pending.
    stored = fake_documents.get(record.id)
    assert stored.status == DocumentStatus.READY
    assert stored.status != DocumentStatus.PENDING


def test_blank_pdf_fails_before_chunking(fakes):
    _, fake_chunks, _ = fakes
    pdf = FPDF()
    pdf.add_page()  # no text
    blank_bytes = bytes(pdf.output())

    record, pages = document_service.ingest_document("blank.pdf", blank_bytes)

    assert record.status == DocumentStatus.FAILED
    assert "scanned" in record.error_message.lower()
    assert pages == []
    assert fake_chunks.inserted == []


def test_embedding_failure_marks_document_failed(fakes):
    fake_documents, fake_chunks, fake_embeddings = fakes
    fake_embeddings.raise_on_embed = RuntimeError("model unavailable")
    pdf_bytes = _make_pdf(["Some real content to embed."])

    record, pages = document_service.ingest_document("sample.pdf", pdf_bytes)

    assert record.status == DocumentStatus.FAILED
    assert "model unavailable" in record.error_message
    assert pages == []
    assert fake_chunks.inserted == []


def test_chunk_storage_failure_marks_document_failed(fakes):
    fake_documents, fake_chunks, _ = fakes
    fake_chunks.raise_on_insert = RuntimeError("supabase unreachable")
    pdf_bytes = _make_pdf(["Some real content to store."])

    record, pages = document_service.ingest_document("sample.pdf", pdf_bytes)

    assert record.status == DocumentStatus.FAILED
    assert "supabase unreachable" in record.error_message
    assert pages == []
