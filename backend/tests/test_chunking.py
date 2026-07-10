"""Tests for chunking logic — pure function, no external dependencies."""

from app.models.document import PageText
from app.services.chunking import chunk_document


def test_chunks_stay_within_page_and_preserve_page_number():
    pages = [
        PageText(page_number=1, text=" ".join(f"word{i}" for i in range(250))),
        PageText(page_number=2, text=" ".join(f"word{i}" for i in range(50))),
    ]

    chunks = chunk_document(pages, chunk_size_words=200, chunk_overlap_words=30)

    assert all(c.page_number in (1, 2) for c in chunks)
    page_1_chunks = [c for c in chunks if c.page_number == 1]
    page_2_chunks = [c for c in chunks if c.page_number == 2]
    assert len(page_1_chunks) >= 2  # 250 words > chunk_size, must split
    assert len(page_2_chunks) == 1  # 50 words fits in one chunk


def test_chunk_indices_are_sequential_across_pages():
    pages = [
        PageText(page_number=1, text="hello world"),
        PageText(page_number=2, text="more text here"),
    ]

    chunks = chunk_document(pages, chunk_size_words=200, chunk_overlap_words=30)

    indices = [c.chunk_index for c in chunks]
    assert indices == list(range(len(chunks)))


def test_empty_pages_produce_no_chunks():
    pages = [PageText(page_number=1, text=""), PageText(page_number=2, text="   ")]

    chunks = chunk_document(pages, chunk_size_words=200, chunk_overlap_words=30)

    assert chunks == []


def test_overlap_repeats_words_between_consecutive_chunks():
    words = [f"w{i}" for i in range(20)]
    pages = [PageText(page_number=1, text=" ".join(words))]

    chunks = chunk_document(pages, chunk_size_words=10, chunk_overlap_words=4)

    assert len(chunks) >= 2
    first_words = chunks[0].chunk_text.split()
    second_words = chunks[1].chunk_text.split()
    overlap = set(first_words[-4:]) & set(second_words[:4])
    assert len(overlap) > 0
