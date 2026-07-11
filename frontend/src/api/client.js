/**
 * Campus Genius API client.
 *
 * Mirrors the backend contract exactly (see backend/app/api/*.py,
 * backend/app/models/*.py). Every field name here matches a Pydantic
 * response model field 1:1 - nothing invented on top of it.
 *
 * Note: the backend has no "list all documents" endpoint, only
 * POST /documents/upload and GET /documents/{id}. Document history is
 * therefore tracked client-side (see hooks/useDocumentLibrary in App.jsx).
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* response wasn't JSON */
    }
    throw new ApiError(detail, res.status);
  }
  return res.json();
}

/** GET /health */
export function getHealth() {
  return request("/health");
}

/** POST /documents/upload (multipart) -> DocumentResponse */
export function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/documents/upload", {
    method: "POST",
    body: formData,
  });
}

/** GET /documents/{document_id} -> DocumentResponse */
export function getDocument(documentId) {
  return request(`/documents/${documentId}`);
}

/** POST /retrieval/search -> RetrievedChunk[] */
export function searchChunks({ query, topK, documentId }) {
  return request("/retrieval/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      top_k: topK,
      document_id: documentId || null,
    }),
  });
}

/** POST /answer/ask -> AnswerResponse */
export function askQuestion({ query, topK, documentId }) {
  return request("/answer/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      top_k: topK,
      document_id: documentId || null,
    }),
  });
}

/** POST /viva/generate -> VivaResponse */
export function generateViva({ documentId, numQuestions, chunkLimit }) {
  return request("/viva/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      document_id: documentId,
      num_questions: numQuestions,
      chunk_limit: chunkLimit,
    }),
  });
}

export { ApiError };
