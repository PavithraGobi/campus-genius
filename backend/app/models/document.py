"""Document-related schemas.

Mirrors the shape of the `documents` table defined in the Supabase schema
(see PROJECT_REQUIREMENTS.md / ARCHITECTURE.md), so swapping the in-memory
store for a real Supabase-backed store later is a drop-in change.
"""

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class PageText(BaseModel):
    page_number: int
    text: str


class DocumentRecord(BaseModel):
    """Internal representation held by the document store."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    file_path: str
    status: DocumentStatus = DocumentStatus.PENDING
    language_hint: str | None = None
    page_count: int | None = None
    file_size_bytes: int
    error_message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DocumentResponse(BaseModel):
    """Public-facing response shape returned by the API."""

    id: str
    filename: str
    status: DocumentStatus
    page_count: int | None = None
    file_size_bytes: int
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: DocumentRecord) -> "DocumentResponse":
        return cls(
            id=record.id,
            filename=record.filename,
            status=record.status,
            page_count=record.page_count,
            file_size_bytes=record.file_size_bytes,
            error_message=record.error_message,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
