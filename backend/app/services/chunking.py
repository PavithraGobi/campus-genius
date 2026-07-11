"""Text chunking.

Chunks are produced per page (never spanning page boundaries) so each
chunk's `page_number` stays exact and simple — matching the retrieval
design in ARCHITECTURE.md ("prefer short, relevant chunks", "optionally
filter by page number").

Splitting is word-based (via str.split()) rather than character-based,
since it keeps whole words intact for both English and Tamil text, and
avoids pulling in an extra tokenizer dependency for this phase.
"""

from app.models.chunk import ChunkDraft
from app.models.document import PageText


def _chunk_words(words: list[str], chunk_size: int, overlap: int) -> list[list[str]]:
    if not words:
        return []

    step = max(chunk_size - overlap, 1)
    chunks = []
    start = 0
    while start < len(words):
        chunks.append(words[start : start + chunk_size])
        if start + chunk_size >= len(words):
            break
        start += step
    return chunks


def chunk_document(
    pages: list[PageText],
    chunk_size_words: int,
    chunk_overlap_words: int,
) -> list[ChunkDraft]:
    """Chunk every page's text, returning drafts with a global chunk_index."""
    drafts: list[ChunkDraft] = []
    chunk_index = 0

    for page in pages:
        words = page.text.split()
        if not words:
            continue

        for word_chunk in _chunk_words(words, chunk_size_words, chunk_overlap_words):
            drafts.append(
                ChunkDraft(
                    chunk_index=chunk_index,
                    page_number=page.page_number,
                    chunk_text=" ".join(word_chunk),
                )
            )
            chunk_index += 1

    return drafts