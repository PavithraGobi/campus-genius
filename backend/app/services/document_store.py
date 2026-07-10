"""Document metadata persistence — Supabase-backed.

Same method signatures as the Phase 3 in-memory version, so
document_service.py didn't need to change to use this.
"""

from app.core.supabase_client import get_supabase_client
from app.models.document import DocumentRecord, DocumentStatus

TABLE = "documents"


class DocumentStore:
    def create(self, record: DocumentRecord) -> DocumentRecord:
        client = get_supabase_client()
        payload = {
            "id": record.id,
            "filename": record.filename,
            "file_path": record.file_path,
            "status": record.status.value,
            "language_hint": record.language_hint,
            "page_count": record.page_count,
            "file_size_bytes": record.file_size_bytes,
            "error_message": record.error_message,
        }
        client.table(TABLE).insert(payload).execute()
        return record

    def get(self, document_id: str) -> DocumentRecord | None:
        client = get_supabase_client()
        response = client.table(TABLE).select("*").eq("id", document_id).execute()
        rows = response.data
        if not rows:
            return None
        return DocumentRecord(**rows[0])

    def update_status(
        self,
        document_id: str,
        status: DocumentStatus,
        *,
        page_count: int | None = None,
        error_message: str | None = None,
    ) -> DocumentRecord | None:
        client = get_supabase_client()
        payload: dict = {"status": status.value, "error_message": error_message}
        if page_count is not None:
            payload["page_count"] = page_count

        response = (
            client.table(TABLE).update(payload).eq("id", document_id).execute()
        )
        rows = response.data
        if not rows:
            return None
        return DocumentRecord(**rows[0])


document_store = DocumentStore()
