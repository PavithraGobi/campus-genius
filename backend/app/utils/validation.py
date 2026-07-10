"""Upload validation helpers."""

from fastapi import UploadFile

PDF_MAGIC_BYTES = b"%PDF-"


class UploadValidationError(Exception):
    """Raised when an uploaded file fails validation."""


def validate_pdf_upload(file: UploadFile, contents: bytes, max_size_mb: int) -> None:
    """Validate file extension, declared content type, magic bytes, and size.

    Raises UploadValidationError with a human-readable message on failure.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise UploadValidationError("Only .pdf files are accepted.")

    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise UploadValidationError(f"Unsupported content type: {file.content_type}")

    if not contents.startswith(PDF_MAGIC_BYTES):
        raise UploadValidationError("File does not appear to be a valid PDF.")

    max_size_bytes = max_size_mb * 1024 * 1024
    if len(contents) > max_size_bytes:
        raise UploadValidationError(f"File exceeds the {max_size_mb}MB size limit.")

    if len(contents) == 0:
        raise UploadValidationError("Uploaded file is empty.")
