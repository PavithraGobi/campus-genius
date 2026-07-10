"""API-level tests for document upload/status endpoints.

Uses fakes for the Supabase stores and embedding model (patched on the
document_service module, which both endpoints go through) so these run
without real network access.
"""

import pytest
from fastapi.testclient import TestClient
from fpdf import FPDF

from app.core.config import settings
from app.services import document_service
from main import app
from tests.fakes import FakeChunkStore, FakeDocumentStore, FakeEmbeddingService

client = TestClient(app)


def _make_pdf(pages_text: list[str]) -> bytes:
    pdf = FPDF()
    for text in pages_text:
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, text)
    return bytes(pdf.output())


@pytest.fixture(autouse=True)
def fakes(monkeypatch, tmp_path):
    monkeypatch.setattr(document_service, "document_store", FakeDocumentStore())
    monkeypatch.setattr(document_service, "chunk_store", FakeChunkStore())
    monkeypatch.setattr(document_service, "embedding_service", FakeEmbeddingService(dim=8))
    monkeypatch.setattr(document_service.settings, "upload_dir", str(tmp_path))


def test_upload_valid_pdf_extracts_text_and_becomes_ready():
    pdf_bytes = _make_pdf(["Page one content.", "Page two content."])

    response = client.post(
        "/documents/upload",
        files={"file": ("sample.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ready"
    assert body["page_count"] == 2
    assert body["error_message"] is None


def test_get_document_returns_stored_status():
    pdf_bytes = _make_pdf(["Some content."])
    upload = client.post(
        "/documents/upload",
        files={"file": ("sample.pdf", pdf_bytes, "application/pdf")},
    )
    doc_id = upload.json()["id"]

    response = client.get(f"/documents/{doc_id}")

    assert response.status_code == 200
    assert response.json()["id"] == doc_id
    assert response.json()["status"] == "ready"


def test_get_unknown_document_returns_404():
    response = client.get("/documents/does-not-exist")
    assert response.status_code == 404


def test_rejects_non_pdf_file():
    response = client.post(
        "/documents/upload",
        files={"file": ("notes.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 400
    assert "pdf" in response.json()["detail"].lower()


def test_rejects_oversized_file():
    pdf_bytes = _make_pdf(["Some content."])
    original_limit = settings.max_upload_size_mb
    settings.max_upload_size_mb = 0
    try:
        response = client.post(
            "/documents/upload",
            files={"file": ("big.pdf", pdf_bytes, "application/pdf")},
        )
        assert response.status_code == 400
        assert "size limit" in response.json()["detail"].lower()
    finally:
        settings.max_upload_size_mb = original_limit


def test_blank_pdf_with_no_text_marks_document_failed():
    pdf = FPDF()
    pdf.add_page()  # no text added
    blank_bytes = bytes(pdf.output())

    response = client.post(
        "/documents/upload",
        files={"file": ("blank.pdf", blank_bytes, "application/pdf")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "failed"
    assert body["error_message"] is not None
    assert "scanned" in body["error_message"].lower()


def test_rejects_empty_file():
    response = client.post(
        "/documents/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400
