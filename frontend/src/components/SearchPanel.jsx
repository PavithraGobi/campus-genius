import { useState } from "react";
import { FileText, Search as SearchIcon, SlidersHorizontal } from "lucide-react";
import { searchChunks } from "../api/client.js";
import ErrorState from "./ErrorState.jsx";
import AnswerSkeleton from "./AnswerSkeleton.jsx";
import { getStoredDefaultTopK } from "../lib/preferences.js";

function escapeRegExp(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function highlight(text, query) {
  const q = query.trim();
  if (!q) return text;
  const words = [...new Set(q.split(/\s+/).filter((w) => w.length > 1))];
  if (words.length === 0) return text;
  const pattern = new RegExp(`(${words.map(escapeRegExp).join("|")})`, "gi");
  return text.split(pattern).map((part, i) =>
    words.some((w) => w.toLowerCase() === part.toLowerCase()) ? (
      <mark key={i}>{part}</mark>
    ) : (
      <span key={i}>{part}</span>
    ),
  );
}

export default function SearchPanel({ documents }) {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [documentId, setDocumentId] = useState("");
  // Starting value comes from Settings > Retrieval defaults; still a
  // per-query override like before, just a better starting point.
  const [topK, setTopK] = useState(getStoredDefaultTopK);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  const readyDocs = documents.filter((d) => d.status === "ready");

  function labelFor(id) {
    return documents.find((d) => d.id === id)?.filename;
  }

  function clearScope() {
    setDocumentId("");
  }

  async function runQuery(params) {
    setLoading(true);
    setError(null);
    setResults(null);
    setHasSearched(true);
    setSubmittedQuery(params.query);
    try {
      const chunks = await searchChunks(params);
      setResults(chunks);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!query.trim()) return;
    runQuery({ query, topK, documentId });
  }

  function handleRetry() {
    runQuery({ query, topK, documentId });
  }

  const docCount = new Set((results || []).map((c) => c.document_id)).size;

  return (
    <section className="panel">
      <header className="panel-header">
        <h1>Search across documents</h1>
        <p>Hybrid retrieval over your library - no answer generation, just the ranked chunks.</p>
      </header>

      <form onSubmit={handleSubmit}>
        <div className="search-hero">
          <SearchIcon size={16} />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search all documents…"
            aria-label="Search chunk text"
          />
          <button className="search-hero-submit" type="submit" disabled={loading || !query.trim()}>
            {loading ? "Searching…" : "Search"}
          </button>
        </div>

        <div className="search-filters">
          <span className="scope-pill">
            <FileText size={13} />
            <select value={documentId} onChange={(e) => setDocumentId(e.target.value)}>
              <option value="">All ready documents</option>
              {readyDocs.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.filename}
                </option>
              ))}
            </select>
            {documentId && (
              <button
                type="button"
                className="scope-pill-clear"
                onClick={clearScope}
                aria-label="Clear document filter"
              >
                ×
              </button>
            )}
          </span>
          <span className="scope-pill scope-pill-topk">
            <SlidersHorizontal size={13} />
            <span className="scope-pill-topk-label">Top K</span>
            <input
              type="number"
              min={1}
              max={50}
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              aria-label="Number of chunks retrieved"
            />
          </span>
        </div>
      </form>

      {!hasSearched && !loading && (
        <div className="empty-panel-state">
          <p>Search for text above to see the ranked chunks a query would retrieve.</p>
        </div>
      )}

      {loading && <AnswerSkeleton />}

      {!loading && error && <ErrorState error={error} onRetry={handleRetry} />}

      {!loading && results && (
        <>
          <div className="search-meta-row">
            <span>
              {results.length} match{results.length === 1 ? "" : "es"}
            </span>
            {results.length > 0 && (
              <>
                <span>·</span>
                <span>
                  Across {docCount} document{docCount === 1 ? "" : "s"}
                </span>
              </>
            )}
          </div>
          {results.length === 0 ? (
            <div className="empty-state">No matching chunks.</div>
          ) : (
            <div className="result-list">
              {results.map((chunk, i) => (
                <article key={chunk.chunk_id} className="result-card" style={{ "--stagger": i }}>
                  <div className="result-card-head">
                    <div className="result-card-doc">
                      <FileText size={15} />
                      <span>{labelFor(chunk.document_id) || chunk.document_id}</span>
                    </div>
                    <span className="result-card-pill">Page {chunk.page_number}</span>
                  </div>
                  <p className="result-card-snippet">{highlight(chunk.chunk_text, submittedQuery)}</p>
                  <div className="result-card-foot">
                    <span>{Math.round(chunk.similarity_score * 100)}% match</span>
                    <span>chunk #{chunk.chunk_index}</span>
                  </div>
                </article>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  );
}
