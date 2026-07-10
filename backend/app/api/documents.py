"""Document upload and status endpoints."""

from fastapi import APIRouter, HTTPException, UploadFile

from app.core.config import settings
from app.models.document import DocumentResponse
from app.services import document_service
from app.utils.validation import UploadValidationError, validate_pdf_upload

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(file: UploadFile) -> DocumentResponse:
    contents = await file.read()

    try:
        validate_pdf_upload(file, contents, settings.max_upload_size_mb)
    except UploadValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    record, _pages = document_service.ingest_document(file.filename, contents)
    return DocumentResponse.from_record(record)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str) -> DocumentResponse:
    record = document_service.document_store.get(document_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentResponse.from_record(record)
