"""Document ingestion orchestration.

Flow: save file -> pending -> processing -> extract text -> chunk ->
embed -> persist chunks -> ready. Any failure along the way marks the
document failed with a clear error_message instead of leaving it stuck
or raising an unhandled error.
"""

from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.models.chunk import ChunkRecord
from app.models.document import DocumentRecord, DocumentStatus, PageText
from app.services.chunk_store import chunk_store
from app.services.chunking import chunk_document
from app.services.document_store import document_store
from app.services.embedding_service import embedding_service
from app.services.pdf_extraction import PDFExtractionError, extract_text_by_page


def _save_file(filename: str, contents: bytes) -> str:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_suffix = Path(filename).suffix or ".pdf"
    stored_name = f"{uuid4()}{safe_suffix}"
    file_path = upload_dir / stored_name

    file_path.write_bytes(contents)
    return str(file_path)


def ingest_document(filename: str, contents: bytes) -> tuple[DocumentRecord, list[PageText]]:
    """Save, extract, chunk, embed, and persist a document end to end.

    Returns the final document record plus the extracted pages (empty
    list if any step failed).
    """
    file_path = _save_file(filename, contents)

    record = DocumentRecord(
        filename=filename,
        file_path=file_path,
        file_size_bytes=len(contents),
        status=DocumentStatus.PENDING,
    )
    document_store.create(record)
    document_store.update_status(record.id, DocumentStatus.PROCESSING)

    try:
        pages = extract_text_by_page(file_path)
    except PDFExtractionError as exc:
        updated = document_store.update_status(
            record.id, DocumentStatus.FAILED, error_message=str(exc)
        )
        return updated, []

    chunk_drafts = chunk_document(pages, settings.chunk_size_words, settings.chunk_overlap_words)
    if not chunk_drafts:
        updated = document_store.update_status(
            record.id,
            DocumentStatus.FAILED,
            error_message="No chunkable text was produced from this document.",
        )
        return updated, []

    try:
        embeddings = embedding_service.embed_texts([draft.chunk_text for draft in chunk_drafts])
        chunk_records = [
            ChunkRecord(
                document_id=record.id,
                chunk_index=draft.chunk_index,
                chunk_text=draft.chunk_text,
                embedding=embedding,
                page_number=draft.page_number,
                token_count=len(draft.chunk_text.split()),
            )
            for draft, embedding in zip(chunk_drafts, embeddings)
        ]
        chunk_store.insert_chunks(chunk_records)
    except Exception as exc:
        updated = document_store.update_status(
            record.id,
            DocumentStatus.FAILED,
            error_message=f"Embedding or storage failed: {exc}",
        )
        return updated, []

    updated = document_store.update_status(
        record.id, DocumentStatus.READY, page_count=len(pages)
    )
    return updated, pages
