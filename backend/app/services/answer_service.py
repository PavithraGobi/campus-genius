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

Compound questions (e.g. "what's the difference between X and Y, and what
protocols does Z use?") are handled by retrieving separately per sub-question
and merging the results - see query_decomposition.py. This exists because a
single top_k retrieval pass can silently miss one part of a compound
question on documents where the two topics don't both rank in the same
top_k window; retrieving per-part and merging is a more direct fix than
just asking the model to "try to cover everything" in one pass.
"""

from app.core.config import settings
from app.models.answer import AnswerResponse
from app.models.retrieval import RetrievedChunk
from app.services.ollama_client import ollama_client
from app.services.query_decomposition import decompose_query
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
- If the question is presented as multiple numbered parts, address EVERY part explicitly - do not skip or gloss over any of them.
- If asked for a DIFFERENCE or COMPARISON between items, state the specific distinguishing characteristic of EACH item (e.g. scope, size, function) - do not just list or name the items without explaining how they differ.
- Keep the answer concise, clear, and grammatically correct.
- Do not invent citations.
- Do not add trailing meta sentences or broken punctuation.
- Respond in the SAME language(s) as the question. If the question is in Tamil, answer in Tamil. If it mixes Tamil and English (Tanglish), answer in that same mix. Never respond in any other language (e.g. Chinese) under any circumstance.
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


def _build_user_prompt(sub_questions: list[str], chunks: list[RetrievedChunk]) -> str:
    context_blocks = "\n\n".join(
        f"[{i}] (Page {chunk.page_number})\n{chunk.chunk_text}"
        for i, chunk in enumerate(chunks, start=1)
    )

    # Single question: identical output to before this feature existed -
    # no behavior change at all for the common case (this is the path
    # Test 1 and Test 2 already pass through).
    if len(sub_questions) == 1:
        return f"Context:\n{context_blocks}\n\nQuestion: {sub_questions[0]}\n\nAnswer:"

    numbered = "\n".join(f"{i}. {q}" for i, q in enumerate(sub_questions, start=1))
    return (
        f"Context:\n{context_blocks}\n\n"
        f"This question has {len(sub_questions)} parts:\n{numbered}\n\n"
        "Answer each part clearly, using only the context above. If a part "
        "isn't covered by the context, say so specifically for that part.\n\n"
        "Answer:"
    )


def _merge_chunks(chunk_lists: list[list[RetrievedChunk]]) -> list[RetrievedChunk]:
    """Dedupe chunks retrieved across multiple sub-questions, keep best score."""
    by_id: dict[str, RetrievedChunk] = {}
    for chunks in chunk_lists:
        for chunk in chunks:
            existing = by_id.get(chunk.chunk_id)
            if existing is None or chunk.similarity_score > existing.similarity_score:
                by_id[chunk.chunk_id] = chunk
    return sorted(by_id.values(), key=lambda c: c.similarity_score, reverse=True)


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

    sub_questions = decompose_query(query)

    if len(sub_questions) == 1:
        # Fast path, unchanged from before decomposition existed.
        chunks = retrieve_relevant_chunks(query=query, top_k=top_k, document_id=document_id)
    else:
        per_question_chunks = [
            retrieve_relevant_chunks(query=q, top_k=top_k, document_id=document_id)
            for q in sub_questions
        ]
        chunks = _merge_chunks(per_question_chunks)

    if not chunks or chunks[0].similarity_score < settings.min_similarity_threshold:
        return AnswerResponse(
            answer=INSUFFICIENT_CONTEXT_MESSAGE,
            sources=[],
            insufficient_context=True,
        )

    user_prompt = _build_user_prompt(sub_questions, chunks)
    answer_text = ollama_client.chat(SYSTEM_PROMPT, user_prompt)

    return AnswerResponse(
        answer=answer_text,
        sources=chunks,
        insufficient_context=False,
    )