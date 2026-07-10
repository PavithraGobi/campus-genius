"""Answer generation endpoint — retrieval + Ollama, grounded answers."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.answer import AnswerResponse
from app.services.answer_service import generate_answer
from app.services.ollama_client import OllamaUnavailableError

router = APIRouter(prefix="/answer", tags=["answer"])


class AskRequest(BaseModel):
    query: str
    top_k: int = Field(default=settings.retrieval_default_top_k, ge=1, le=50)
    document_id: str | None = None


@router.post("/ask", response_model=AnswerResponse)
def ask(request: AskRequest) -> AnswerResponse:
    try:
        return generate_answer(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OllamaUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
