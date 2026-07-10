"""Retrieval endpoint — search for relevant chunks given a query.

No answer generation here (that's Phase 6) — this returns raw chunks so
retrieval quality can be inspected/tested on its own.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.retrieval import RetrievedChunk
from app.services.retrieval_service import retrieve_relevant_chunks

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=settings.retrieval_default_top_k, ge=1, le=50)
    document_id: str | None = None


@router.post("/search", response_model=list[RetrievedChunk])
def search(request: SearchRequest) -> list[RetrievedChunk]:
    try:
        return retrieve_relevant_chunks(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
