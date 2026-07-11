"""Viva question generation schemas."""

from enum import Enum

from pydantic import BaseModel


class VivaDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class VivaQuestion(BaseModel):
    question: str
    difficulty: VivaDifficulty
    source_pages: list[int]


class VivaResponse(BaseModel):
    questions: list[VivaQuestion]
    insufficient_context: bool
