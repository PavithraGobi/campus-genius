"""Answer generation schemas."""

from pydantic import BaseModel

from app.models.retrieval import RetrievedChunk


class AnswerResponse(BaseModel):
    answer: str
    sources: list[RetrievedChunk]
    insufficient_context: bool
