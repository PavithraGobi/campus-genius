import { useMemo, useRef, useState } from "react";
import { AlertTriangle, CheckCircle2, FileText, Upload as UploadIcon } from "lucide-react";
import { uploadDocument, ApiError } from "../api/client.js";
import StatusBadge from "./StatusBadge.jsx";

function formatBytes(bytes) {
  if (bytes == null) return null;
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const STATUS_TEXT = {
  pending: "Queued for processing…",
  processing: "Chunking and embedding pages…",
  ready: "Ready to query",
  failed: "Processing failed",
};

export default function UploadPanel({ documents, onUploaded, onAsk, onOpenLibrary }) {
  const [dragState, setDragState] = useState("idle"); // idle | active | invalid
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [lastDocId, setLastDocId] = useState(null);
  const inputRef = useRef(null);

  // Live status of the file just uploaded - useDocumentLibrary already
  // polls pending/processing documents, so this updates on its own as
  // the backend finishes chunking and embedding, no fake progress bar.
  const lastDoc = useMemo(
    () => documents.find((d) => d.id === lastDocId) || null,
    [documents, lastDocId],
  );

  async function handleFile(file) {
    if (!file) return;
    if (file.type !== "application/pdf") {
      setError(`"${file.name}" isn't a PDF - only PDF files can be uploaded.`);
      return;
    }
    setError(null);
    setUploading(true);
    try {
      const doc = await uploadDocument(file);
      onUploaded(doc);
      setLastDocId(doc.id);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Upload failed - is the backend running?";
      setError(message);
    } finally {
      setUploading(false);
    }
  }

  function dragFileType(e) {
    return e.dataTransfer.items?.[0]?.type;
  }

  return (
    <section className="panel">
      <header className="panel-header">
        <h1>Upload a document</h1>
        <p>Add a course PDF. It's chunked and embedded before it's ready to query.</p>
      </header>

      <div
        className={`dropzone dropzone-hero is-${dragState}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragState(dragFileType(e) === "application/pdf" ? "active" : "invalid");
        }}
        onDragLeave={() => setDragState("idle")}
        onDrop={(e) => {
          e.preventDefault();
          setDragState("idle");
          handleFile(e.dataTransfer.files?.[0]);
        }}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          hidden
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        <div className="dropzone-mark dropzone-mark-lg" aria-hidden="true">
          {dragState === "invalid" ? <AlertTriangle size={22} /> : <UploadIcon size={22} />}
        </div>
        <h2 className="dropzone-title">
          {dragState === "invalid" ? "Only PDF files are supported" : "Drop your PDF here"}
        </h2>
        <p className="dropzone-text dropzone-text-lg">
          or click below to browse your files
        </p>
        <button
          type="button"
          className="primary-button"
          onClick={() => inputRef.current?.click()}
          disabled={uploading}
        >
          <UploadIcon size={14} style={{ marginRight: "0.4rem", verticalAlign: "-2px" }} />
          {uploading ? "Uploading…" : "Choose file"}
        </button>
        <div className="dropzone-hint dropzone-hint-row">
          <span>PDF only</span>
        </div>
      </div>

      {error && <div className="inline-error">{error}</div>}

      {lastDoc && (
        <div className="upload-preview">
          <div className="upload-preview-icon">
            <FileText size={19} />
          </div>
          <div className="upload-preview-main">
            <div className="upload-preview-head">
              <div className="upload-preview-name" title={lastDoc.filename}>
                {lastDoc.filename}
              </div>
              {lastDoc.status === "ready" && (
                <span className="upload-preview-pill upload-preview-pill-success">
                  <CheckCircle2 size={13} /> Uploaded
                </span>
              )}
              {lastDoc.status === "failed" && (
                <span className="upload-preview-pill upload-preview-pill-error">
                  <AlertTriangle size={13} /> Failed
                </span>
              )}
              {(lastDoc.status === "pending" || lastDoc.status === "processing") && (
                <StatusBadge status={lastDoc.status} />
              )}
            </div>
            <div className="upload-preview-meta">
              {[formatBytes(lastDoc.file_size_bytes), STATUS_TEXT[lastDoc.status]]
                .filter(Boolean)
                .join(" · ")}
            </div>

            {lastDoc.status === "failed" && lastDoc.error_message && (
              <div className="doc-grid-error">{lastDoc.error_message}</div>
            )}

            {(lastDoc.status === "pending" || lastDoc.status === "processing") && (
              <div className="upload-preview-bar">
                <div className="upload-preview-bar-fill" />
              </div>
            )}

            {lastDoc.status === "ready" && (
              <div className="upload-preview-actions">
                <button className="primary-button primary-button-sm" onClick={() => onAsk?.(lastDoc.id)}>
                  Ask a question
                </button>
                <button className="ghost-button" onClick={onOpenLibrary}>
                  Open library
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="upload-tips">
        <h3>Tips for best results</h3>
        <ul>
          <li>Text-based PDFs chunk and embed the fastest.</li>
          <li>Split very long books into chapters for sharper retrieval.</li>
          <li>Give files descriptive names - they help you find them again in Search and Library.</li>
        </ul>
      </div>
    </section>
  );
}
