"""Viva question generation.

Reuses two existing pieces rather than building new ones:
- `chunk_store.get_ordered_chunks` (Phase 5's storage layer, one small
  addition) for document-scoped content, in reading order rather than
  similarity order — viva needs coverage across the document, not chunks
  relevant to a specific query.
- `ollama_client` (Phase 6) for generation, same as answer_service.

Groundedness is enforced the same way as Phase 6:
1. Deterministically: if the document has no chunks, the LLM is never
   called — an insufficient-context response is returned instead.
2. Via the prompt: the LLM is instructed to use only the given context and
   not invent facts.
"""

import json

from app.core.config import settings
from app.models.viva import VivaQuestion, VivaResponse
from app.services.chunk_store import chunk_store
from app.services.ollama_client import ollama_client

SYSTEM_PROMPT = """You are Campus Genius, generating viva (oral exam) questions from course material.
Rules:
- Base every question ONLY on the provided context.
- Do NOT use outside knowledge.
- Do NOT invent facts not present in the context.
- Generate a mix of easy, medium, and hard questions.
- Each question must be answerable using only the given context.
Output format:
- Respond with ONLY a JSON array. No prose, no markdown fences, no explanation before or after.
- Each item must have exactly these fields:
  "question" (string), "difficulty" ("easy" | "medium" | "hard"), "source_pages" (array of integers).
Example:
[{"question": "What is X?", "difficulty": "easy", "source_pages": [3]}]"""


class VivaGenerationError(Exception):
    """Raised when the model's output can't be parsed into viva questions."""


def _build_user_prompt(chunks: list, num_questions: int) -> str:
    context_blocks = "\n\n".join(
        f"[{i}] (Page {chunk.page_number})\n{chunk.chunk_text}"
        for i, chunk in enumerate(chunks, start=1)
    )
    return (
        f"Context:\n{context_blocks}\n\n"
        f"Generate exactly {num_questions} viva questions from this context."
    )


def _parse_questions(raw_text: str) -> list[VivaQuestion]:
    text = raw_text.strip()

    # Defensive: strip markdown code fences if the model adds them anyway.
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()

    # Defensive: if the model added prose before/after the array despite
    # instructions not to, pull out just the [...] span rather than failing
    # outright. Only applied when the text isn't already clean JSON.
    if not text.startswith("["):
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise VivaGenerationError(f"Model did not return valid JSON: {exc}") from exc

    try:
        return [VivaQuestion(**item) for item in data]
    except (TypeError, ValueError) as exc:
        raise VivaGenerationError(
            f"Model JSON did not match the expected question schema: {exc}"
        ) from exc


def generate_viva_questions(
    document_id: str,
    num_questions: int | None = None,
    chunk_limit: int | None = None,
) -> VivaResponse:
    """Generate grounded viva questions from a document's content.

    Returns an insufficient-context response (no LLM call made) if the
    document has no chunks — same guard style as answer_service.
    """
    num_questions = num_questions or settings.viva_default_num_questions
    chunk_limit = chunk_limit or settings.viva_default_chunk_limit

    chunks = chunk_store.get_ordered_chunks(document_id, limit=chunk_limit)

    if not chunks:
        return VivaResponse(questions=[], insufficient_context=True)

    user_prompt = _build_user_prompt(chunks, num_questions)
    raw_text = ollama_client.chat(SYSTEM_PROMPT, user_prompt)
    questions = _parse_questions(raw_text)

    return VivaResponse(questions=questions, insufficient_context=False)
