function timeAgo(iso) {
  if (!iso) return null;
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.round(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.round(hours / 24)}d ago`;
}

export default function StatusStrip({ health, documents, lastUpload }) {
  const ready = documents.filter((d) => d.status === "ready").length;
  const processing = documents.filter(
    (d) => d.status === "pending" || d.status === "processing"
  ).length;
  const failed = documents.filter((d) => d.status === "failed").length;

  return (
    <div className="status-strip">
      <div className={`status-strip-item status-strip-api status-${health}`}>
        <span className="status-dot" aria-hidden="true" />
        <span>{health === "ok" ? "API connected" : health === "error" ? "API unreachable" : "Checking API…"}</span>
      </div>

      <div className="status-strip-divider" aria-hidden="true" />

      <div className="status-strip-item">
        <span className="status-strip-figure">{ready}</span>
        <span className="status-strip-label">ready</span>
      </div>
      {processing > 0 && (
        <div className="status-strip-item status-strip-item-muted">
          <span className="status-strip-figure">{processing}</span>
          <span className="status-strip-label">processing</span>
        </div>
      )}
      {failed > 0 && (
        <div className="status-strip-item status-strip-item-warn">
          <span className="status-strip-figure">{failed}</span>
          <span className="status-strip-label">failed</span>
        </div>
      )}

      <div className="status-strip-divider" aria-hidden="true" />

      <div className="status-strip-item status-strip-upload">
        {lastUpload ? (
          <>
            <span className="status-strip-label">last upload</span>
            <span className="status-strip-upload-name">{lastUpload.filename}</span>
            <span className="status-strip-label">{timeAgo(lastUpload.uploadedAt)}</span>
          </>
        ) : (
          <span className="status-strip-label">no uploads yet</span>
        )}
      </div>
    </div>
  );
}
