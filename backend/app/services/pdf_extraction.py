"""PDF text extraction.

Extracts text per page, preserving page numbers for later citation use
(see ARCHITECTURE.md's `chunks.page_number` field).
"""

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.models.document import PageText


class PDFExtractionError(Exception):
    """Raised when a PDF cannot be read or contains no extractable text."""


def extract_text_by_page(file_path: str) -> list[PageText]:
    """Extract text from each page of a PDF.

    Raises PDFExtractionError if the file can't be parsed, or if no page
    yields any extractable text — the latter is the fallback signal for
    scanned/image-only PDFs, which need OCR (not yet supported; see
    README.md Future Work).
    """
    try:
        reader = PdfReader(file_path)
    except (PdfReadError, OSError) as exc:
        raise PDFExtractionError(f"Could not read PDF file: {exc}") from exc

    if len(reader.pages) == 0:
        raise PDFExtractionError("PDF has no pages.")

    pages: list[PageText] = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # pypdf can raise various parsing errors per-page
            raise PDFExtractionError(f"Failed to extract text from page {index}: {exc}") from exc
        pages.append(PageText(page_number=index, text=text.strip()))

    if all(not page.text for page in pages):
        raise PDFExtractionError(
            "No extractable text found in this PDF. It may be a scanned or "
            "image-only document — OCR is not yet supported."
        )

    return pages
