"""Answer generation.

Wires Phase 5 retrieval to Ollama: retrieve relevant chunks, and if they're
actually relevant enough, ask the LLM to answer using only that context.

Groundedness is enforced two ways:
1. Deterministically: if no chunks are retrieved, or the best match is
   below `min_similarity_threshold`, the LLM is never called at all — we
   return a clear "not enough information" answer instead.
2. Via the prompt: the LLM is explicitly instructed to say so if the
   provided context doesn't answer the question, rather than guessing.
Neither layer is perfect alone, so both are used together.
"""

from app.core.config import settings
from app.models.answer import AnswerResponse
from app.models.retrieval import RetrievedChunk
from app.services.ollama_client import ollama_client
from app.services.retrieval_service import retrieve_relevant_chunks

INSUFFICIENT_CONTEXT_MESSAGE = (
    "I don't have enough information in the uploaded documents to answer "
    "this question. Please try rephrasing, or upload a document that "
    "covers this topic."
)

SYSTEM_PROMPT = """You are Campus Genius, an academic PDF assistant.
Rules:
- Answer ONLY using the provided context.
- Do NOT use outside knowledge.
- Do NOT infer missing definitions or add extra facts.
- If only part of the question is supported, answer only that part and clearly say what is not covered.
- Keep the answer concise, clear, and grammatically correct.
- Do not invent citations.
- Do not add trailing meta sentences or broken punctuation.
Citation rules:
- When citing, use exactly this format: (Page X)
- Do not write a sentence describing the citation.
- Do not place citation text in a separate sentence by itself.
Language rules:
- If the question is answerable, answer in the user's language or style when possible.
- If the question is not answerable from the context, ignore the language rule and output exactly:
  Insufficient context
- Do NOT translate that phrase.
- Do NOT add any extra text when using that refusal.
Output format:
- If answerable: give a direct grounded answer.
- If not answerable: return only Insufficient context"""


def _build_user_prompt(query: str, chunks: list[RetrievedChunk]) -> str:
    context_blocks = "\n\n".join(
        f"[{i}] (Page {chunk.page_number})\n{chunk.chunk_text}"
        for i, chunk in enumerate(chunks, start=1)
    )
    return f"Context:\n{context_blocks}\n\nQuestion: {query}\n\nAnswer:"


def generate_answer(
    query: str,
    top_k: int | None = None,
    document_id: str | None = None,
) -> AnswerResponse:
    """Retrieve relevant chunks and generate a grounded answer from them.

    Returns an insufficient-context response (no LLM call made) if nothing
    relevant enough was found, rather than risking a hallucinated answer.
    """
    top_k = top_k or settings.retrieval_default_top_k
    chunks = retrieve_relevant_chunks(query=query, top_k=top_k, document_id=document_id)

    if not chunks or chunks[0].similarity_score < settings.min_similarity_threshold:
        return AnswerResponse(
            answer=INSUFFICIENT_CONTEXT_MESSAGE,
            sources=[],
            insufficient_context=True,
        )

    user_prompt = _build_user_prompt(query, chunks)
    answer_text = ollama_client.chat(SYSTEM_PROMPT, user_prompt)

    return AnswerResponse(
        answer=answer_text,
        sources=chunks,
        insufficient_context=False,
    )
