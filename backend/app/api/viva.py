"""Viva question generation endpoint — document-scoped, grounded in retrieved content."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.viva import VivaResponse
from app.services.ollama_client import OllamaUnavailableError
from app.services.viva_service import VivaGenerationError, generate_viva_questions

router = APIRouter(prefix="/viva", tags=["viva"])


class VivaRequest(BaseModel):
    document_id: str
    num_questions: int = Field(default=settings.viva_default_num_questions, ge=1, le=15)
    chunk_limit: int = Field(default=settings.viva_default_chunk_limit, ge=1, le=50)


@router.post("/generate", response_model=VivaResponse)
def generate(request: VivaRequest) -> VivaResponse:
    try:
        return generate_viva_questions(
            document_id=request.document_id,
            num_questions=request.num_questions,
            chunk_limit=request.chunk_limit,
        )
    except OllamaUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except VivaGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
