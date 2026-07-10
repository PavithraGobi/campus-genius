import { useEffect, useState } from "react";
import {
  ArrowUp,
  Check,
  Copy,
  FileText,
  RotateCw,
  Settings2,
  SlidersHorizontal,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
} from "lucide-react";
import { askQuestion } from "../api/client.js";
import ErrorState from "./ErrorState.jsx";
import { getStoredDefaultTopK } from "../lib/preferences.js";

export default function AskPanel({ documents, presetDocumentId }) {
  const [input, setInput] = useState("");
  const [documentId, setDocumentId] = useState("");
  // Starting value comes from Settings > Retrieval defaults; still a
  // per-query override like before, just a better starting point.
  const [topK, setTopK] = useState(getStoredDefaultTopK);
  const [showOptions, setShowOptions] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [linkedIndex, setLinkedIndex] = useState(null);
  const [turns, setTurns] = useState([]); // { question, params, result, feedback }
  const [pendingQuestion, setPendingQuestion] = useState(null);
  const [regeneratingIndex, setRegeneratingIndex] = useState(null);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const readyDocs = documents.filter((d) => d.status === "ready");

  useEffect(() => {
    if (presetDocumentId) {
      setDocumentId(presetDocumentId);
      setShowOptions(true);
    }
  }, [presetDocumentId]);

  function labelFor(id) {
    return documents.find((d) => d.id === id)?.filename;
  }

  function clearScope() {
    setDocumentId("");
  }

  async function runQuery(question, params) {
    setLoading(true);
    setError(null);
    setPendingQuestion(question);
    try {
      const response = await askQuestion(params);
      setTurns((t) => [...t, { question, params, result: response, feedback: null }]);
      setPendingQuestion(null);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }

  function handleSend() {
    if (!input.trim() || loading) return;
    const question = input.trim();
    setInput("");
    runQuery(question, { query: question, topK, documentId });
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleRetry() {
    if (pendingQuestion) runQuery(pendingQuestion, { query: pendingQuestion, topK, documentId });
  }

  function goToSource(turnIndex, n) {
    setLinkedIndex(`${turnIndex}-${n}`);
    const chunkId = turns[turnIndex]?.result?.sources?.[n - 1]?.chunk_id;
    const card = document.getElementById(`chat-source-${turnIndex}-${chunkId}`);
    card?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  async function handleCopy(turnIndex) {
    const text = turns[turnIndex]?.result?.answer;
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(turnIndex);
      setTimeout(() => setCopiedIndex((i) => (i === turnIndex ? null : i)), 1600);
    } catch {
      /* clipboard unavailable - silently ignore, nothing to recover from here */
    }
  }

  async function handleRegenerate(turnIndex) {
    const turn = turns[turnIndex];
    if (!turn || regeneratingIndex !== null) return;
    setRegeneratingIndex(turnIndex);
    setError(null);
    try {
      const response = await askQuestion(turn.params);
      setTurns((t) =>
        t.map((row, i) => (i === turnIndex ? { ...row, result: response, feedback: null } : row)),
      );
    } catch (err) {
      setError(err);
    } finally {
      setRegeneratingIndex(null);
    }
  }

  function handleFeedback(turnIndex, value) {
    setTurns((t) =>
      t.map((row, i) =>
        i === turnIndex ? { ...row, feedback: row.feedback === value ? null : value } : row,
      ),
    );
  }

  const hasThread = turns.length > 0 || pendingQuestion;

  return (
    <section className="panel">
      <header className="panel-header panel-header-row">
        <div>
          <h1>Ask</h1>
          <p>Ask a question. The answer is generated only from retrieved passages, with sources attached.</p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button
            type="button"
            className="ghost-button ask-options-toggle"
            onClick={() => setShowOptions((s) => !s)}
          >
            <Settings2 size={13} style={{ marginRight: "0.35rem", verticalAlign: "-2px" }} />
            Options
          </button>
          {hasThread && (
            <button
              type="button"
              className="ghost-button"
              onClick={() => {
                setTurns([]);
                setError(null);
                setPendingQuestion(null);
                setLinkedIndex(null);
              }}
            >
              New question
            </button>
          )}
        </div>
      </header>

      {showOptions && (
        <div className="ask-options-panel" style={{ marginBottom: "1.5rem" }}>
          <div className="ask-controls">
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
                aria-label="Number of passages retrieved"
              />
            </span>
          </div>
        </div>
      )}

      {!hasThread && !error && (
        <div className="empty-panel-state" style={{ marginBottom: "1.5rem" }}>
          <p>Ask a question below to see a grounded answer with its cited passages here.</p>
        </div>
      )}

      <div className="ask-thread">
        {turns.map((turn, ti) => (
          <ChatTurn
            key={ti}
            turn={turn}
            turnIndex={ti}
            labelFor={labelFor}
            linkedIndex={linkedIndex}
            setLinkedIndex={setLinkedIndex}
            goToSource={goToSource}
            onCopy={handleCopy}
            copied={copiedIndex === ti}
            onRegenerate={handleRegenerate}
            regenerating={regeneratingIndex === ti}
            onFeedback={handleFeedback}
          />
        ))}

        {pendingQuestion && (
          <>
            <div className="chat-msg-user">
              <div className="chat-msg-user-bubble">{pendingQuestion}</div>
            </div>
            {loading && (
              <div className="thinking-row">
                <Sparkles size={14} />
                <span>Reading passages</span>
                <span className="thinking-dots">
                  <span />
                  <span />
                  <span />
                </span>
              </div>
            )}
            {!loading && error && <ErrorState error={error} onRetry={handleRetry} />}
          </>
        )}
      </div>

      <div className="composer">
        <div className="composer-box">
          <div className="composer-row">
            <textarea
              rows={1}
              className="composer-textarea"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about your library…"
            />
            <button
              className="composer-send"
              onClick={handleSend}
              disabled={loading || !input.trim()}
              aria-label="Send question"
            >
              <ArrowUp size={16} />
            </button>
          </div>
          <div className="composer-foot">
            <span>Grounded in your PDFs · Cites pages</span>
            <span>Enter to send · Shift+Enter for newline</span>
          </div>
        </div>
      </div>
    </section>
  );
}

function ChatTurn({
  turn,
  turnIndex,
  labelFor,
  linkedIndex,
  setLinkedIndex,
  goToSource,
  onCopy,
  copied,
  onRegenerate,
  regenerating,
  onFeedback,
}) {
  const { question, result, feedback } = turn;
  return (
    <>
      <div className="chat-msg-user">
        <div className="chat-msg-user-bubble">{question}</div>
      </div>
      <div className="chat-msg-assistant">
        <div className="chat-msg-assistant-head">
          <span className="chat-msg-avatar">
            <Sparkles size={11} />
          </span>
          Campus Genius
          {result.insufficient_context && <span className="pill pill-warn">Low confidence</span>}
        </div>
        <div className="chat-msg-bubble" aria-busy={regenerating}>
          {result.insufficient_context && (
            <div className="insufficient-banner">
              The retrieved passages didn't clear the confidence threshold - treat this answer as
              unverified.
            </div>
          )}
          <p style={{ margin: 0, opacity: regenerating ? 0.45 : 1 }}>
            {result.answer.split(/(\[\d+\])/g).map((part, i) => {
              const match = /^\[(\d+)\]$/.exec(part);
              if (!match) return <span key={i}>{part}</span>;
              const n = Number(match[1]);
              const hasSource = n >= 1 && n <= result.sources.length;
              const key = `${turnIndex}-${n}`;
              return (
                <mark
                  key={i}
                  className={`answer-citation${hasSource ? " is-linked" : ""}`}
                  tabIndex={hasSource ? 0 : undefined}
                  role={hasSource ? "button" : undefined}
                  aria-label={hasSource ? `Jump to source ${n}` : undefined}
                  onMouseEnter={() => hasSource && setLinkedIndex(key)}
                  onMouseLeave={() => hasSource && setLinkedIndex(null)}
                  onFocus={() => hasSource && setLinkedIndex(key)}
                  onBlur={() => hasSource && setLinkedIndex(null)}
                  onClick={() => hasSource && goToSource(turnIndex, n)}
                  onKeyDown={(e) => hasSource && e.key === "Enter" && goToSource(turnIndex, n)}
                >
                  {part}
                </mark>
              );
            })}
          </p>

          {regenerating && (
            <div className="thinking-row" style={{ marginTop: "0.7rem" }}>
              <Sparkles size={13} />
              <span>Regenerating</span>
              <span className="thinking-dots">
                <span />
                <span />
                <span />
              </span>
            </div>
          )}

          {result.sources.length > 0 && (
            <div className="chat-sources">
              <div className="chat-sources-label">
                Sources <span className="section-label-count">{result.sources.length}</span>
              </div>
              <div className="chat-sources-grid">
                {result.sources.map((chunk, i) => (
                  <button
                    key={chunk.chunk_id}
                    id={`chat-source-${turnIndex}-${chunk.chunk_id}`}
                    type="button"
                    className={`chat-source-chip${linkedIndex === `${turnIndex}-${i + 1}` ? " is-highlighted" : ""}`}
                  >
                    <div className="chat-source-chip-head">
                      <FileText size={11} />
                      Page {chunk.page_number}
                    </div>
                    <p className="chat-source-chip-text">{chunk.chunk_text}</p>
                    <div style={{ marginTop: "0.35rem", fontSize: "0.66rem", color: "var(--muted-foreground)" }}>
                      {labelFor(chunk.document_id) || chunk.document_id}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="msg-actions">
          <button
            type="button"
            className="msg-action-btn"
            onClick={() => onCopy(turnIndex)}
            title="Copy"
          >
            {copied ? <Check size={13} /> : <Copy size={13} />}
            <span>{copied ? "Copied" : "Copy"}</span>
          </button>
          <button
            type="button"
            className="msg-action-btn"
            onClick={() => onRegenerate(turnIndex)}
            disabled={regenerating}
            title="Regenerate"
          >
            <RotateCw size={13} className={regenerating ? "is-spinning" : ""} />
            <span>Regenerate</span>
          </button>
          <span className="msg-actions-divider" aria-hidden="true" />
          <button
            type="button"
            className={`msg-action-btn${feedback === "up" ? " is-active" : ""}`}
            onClick={() => onFeedback(turnIndex, "up")}
            title="Helpful"
            aria-pressed={feedback === "up"}
          >
            <ThumbsUp size={13} />
            <span>Helpful</span>
          </button>
          <button
            type="button"
            className={`msg-action-btn${feedback === "down" ? " is-active is-negative" : ""}`}
            onClick={() => onFeedback(turnIndex, "down")}
            title="Not helpful"
            aria-pressed={feedback === "down"}
          >
            <ThumbsDown size={13} />
            <span>Not helpful</span>
          </button>
        </div>
      </div>
    </>
  );
}
