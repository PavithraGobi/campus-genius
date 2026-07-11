import { useState } from "react";
import { FileText, HelpCircle, RotateCw, SlidersHorizontal, Sparkles } from "lucide-react";
import { generateViva } from "../api/client.js";
import ErrorState from "./ErrorState.jsx";

const DIFFICULTY_LABEL = {
  easy: "Easy",
  medium: "Medium",
  hard: "Hard",
};

export default function VivaPanel({ documents }) {
  const [documentId, setDocumentId] = useState("");
  const [numQuestions, setNumQuestions] = useState(6);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const readyDocs = documents.filter((d) => d.status === "ready");

  function labelFor(id) {
    return documents.find((d) => d.id === id)?.filename;
  }

  async function handleGenerate() {
    if (!documentId || loading) return;
    setLoading(true);
    setError(null);
    try {
      const response = await generateViva({ documentId, numQuestions });
      setResult(response);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <header className="panel-header panel-header-row">
        <div>
          <h1>Viva</h1>
          <p>Generate viva questions grounded only in a document's content, not outside knowledge.</p>
        </div>
      </header>

      <div className="ask-options-panel" style={{ marginBottom: "1.5rem" }}>
        <div className="ask-controls">
          <span className="scope-pill">
            <FileText size={13} />
            <select value={documentId} onChange={(e) => setDocumentId(e.target.value)}>
              <option value="">Select a document</option>
              {readyDocs.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.filename}
                </option>
              ))}
            </select>
          </span>
          <span className="scope-pill scope-pill-topk">
            <SlidersHorizontal size={13} />
            <span className="scope-pill-topk-label">Questions</span>
            <input
              type="number"
              min={1}
              max={15}
              value={numQuestions}
              onChange={(e) => setNumQuestions(Number(e.target.value))}
              aria-label="Number of viva questions"
            />
          </span>
          <button
            type="button"
            className="ghost-button"
            onClick={handleGenerate}
            disabled={!documentId || loading}
          >
            <RotateCw size={13} className={loading ? "is-spinning" : ""} style={{ marginRight: "0.35rem", verticalAlign: "-2px" }} />
            {loading ? "Generating" : result ? "Regenerate" : "Generate"}
          </button>
        </div>
      </div>

      {!documentId && !result && (
        <div className="empty-panel-state">
          <p>Pick a document above to generate viva questions from it.</p>
        </div>
      )}

      {loading && (
        <div className="thinking-row">
          <Sparkles size={14} />
          <span>Reading document</span>
          <span className="thinking-dots">
            <span />
            <span />
            <span />
          </span>
        </div>
      )}

      {!loading && error && <ErrorState error={error} onRetry={handleGenerate} />}

      {!loading && result && (
        <div className="answer-block">
          {result.insufficient_context && (
            <div className="insufficient-banner">
              This document doesn't have enough retrievable content to generate viva questions
              from yet.
            </div>
          )}

          {!result.insufficient_context && (
            <div className="result-section">
              <span className="section-label">
                Questions <span className="section-label-count">{result.questions.length}</span>
              </span>
              <div className="ask-thread" style={{ marginTop: "0.75rem" }}>
                {result.questions.map((q, i) => (
                  <article key={i} className="source-card" style={{ "--stagger": i }}>
                    <div className="source-card-fold" aria-hidden="true" />
                    <div className="source-card-perforation" aria-hidden="true" />
                    <div className="source-card-head">
                      <span className="pill">
                        <HelpCircle size={11} style={{ marginRight: "0.3rem", verticalAlign: "-2px" }} />
                        {DIFFICULTY_LABEL[q.difficulty] || q.difficulty}
                      </span>
                      <span className="source-card-score">
                        {q.source_pages.length > 0
                          ? `p. ${q.source_pages.join(", ")}`
                          : "no page ref"}
                      </span>
                    </div>
                    <p className="source-card-text">{q.question}</p>
                    <div className="source-card-foot">
                      <span>{labelFor(documentId) || documentId}</span>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
