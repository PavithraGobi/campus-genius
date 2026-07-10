import { useMemo, useState } from "react";
import { FileText, Grid3x3, List, Search as SearchIcon } from "lucide-react";
import StatusBadge from "./StatusBadge.jsx";

function formatBytes(bytes) {
  if (bytes == null) return null;
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

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

function metaLine(doc) {
  const parts = [];
  parts.push(doc.page_count != null ? `${doc.page_count} pages` : "Pages pending");
  const size = formatBytes(doc.file_size_bytes);
  if (size) parts.push(size);
  const added = timeAgo(doc.created_at);
  if (added) parts.push(`added ${added}`);
  return parts.join(" · ");
}

export default function LibraryPanel({ documents, onRefresh, onAsk }) {
  const [view, setView] = useState("grid");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("recent");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let list = q ? documents.filter((d) => d.filename.toLowerCase().includes(q)) : documents;
    list = [...list];
    if (sort === "az") {
      list.sort((a, b) => a.filename.localeCompare(b.filename));
    } else if (sort === "pages") {
      list.sort((a, b) => (b.page_count || 0) - (a.page_count || 0));
    } else {
      list.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
    }
    return list;
  }, [documents, query, sort]);

  const totalPages = documents.reduce((sum, d) => sum + (d.page_count || 0), 0);

  return (
    <section className="panel">
      <header className="panel-header">
        <h1>Library</h1>
        <p>
          {documents.length} document{documents.length === 1 ? "" : "s"}
          {totalPages > 0 && ` · ${totalPages} pages indexed`}
        </p>
      </header>

      {documents.length === 0 ? (
        <EmptyLibrary />
      ) : (
        <>
          <div className="library-toolbar">
            <label className="library-search">
              <SearchIcon size={15} />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search documents…"
                aria-label="Search documents"
              />
            </label>
            <select
              className="library-sort"
              value={sort}
              onChange={(e) => setSort(e.target.value)}
              aria-label="Sort documents"
            >
              <option value="recent">Sort: Recently added</option>
              <option value="az">Sort: A → Z</option>
              <option value="pages">Sort: Most pages</option>
            </select>
            <div className="view-toggle" role="group" aria-label="Change view">
              <button
                type="button"
                className={`view-toggle-btn${view === "grid" ? " is-active" : ""}`}
                onClick={() => setView("grid")}
                aria-pressed={view === "grid"}
                aria-label="Grid view"
              >
                <Grid3x3 size={15} />
              </button>
              <button
                type="button"
                className={`view-toggle-btn${view === "list" ? " is-active" : ""}`}
                onClick={() => setView("list")}
                aria-pressed={view === "list"}
                aria-label="List view"
              >
                <List size={15} />
              </button>
            </div>
          </div>

          {filtered.length === 0 ? (
            <div className="empty-panel-state">
              <p>No documents match "{query}".</p>
            </div>
          ) : view === "grid" ? (
            <div className="doc-grid">
              {filtered.map((doc, i) => (
                <DocGridCard
                  key={doc.id}
                  doc={doc}
                  index={i}
                  onRefresh={onRefresh}
                  onAsk={onAsk}
                />
              ))}
            </div>
          ) : (
            <div className="doc-list-panel">
              {filtered.map((doc) => (
                <div key={doc.id} className="doc-list-row">
                  <div className="doc-list-icon">
                    <FileText size={16} />
                  </div>
                  <div className="doc-list-main">
                    <div className="doc-list-title">{doc.filename}</div>
                    <div className="doc-list-meta">{metaLine(doc)}</div>
                    {doc.error_message && <div className="doc-grid-error">{doc.error_message}</div>}
                  </div>
                  <StatusBadge status={doc.status} />
                  <button className="ghost-button" onClick={() => onRefresh(doc.id)}>
                    Refresh
                  </button>
                  {doc.status === "ready" && onAsk && (
                    <button className="doc-grid-ask" onClick={() => onAsk(doc.id)}>
                      Ask AI →
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  );
}

function DocGridCard({ doc, index, onRefresh, onAsk }) {
  const citation = index % 2 === 1;
  return (
    <article className="doc-grid-card" style={{ "--stagger": index }}>
      <div className={`doc-grid-thumb${citation ? " is-citation" : ""}`}>
        <FileText size={15} className="doc-grid-thumb-icon" />
        <div className="doc-grid-thumb-lines" aria-hidden="true">
          <span style={{ width: "75%" }} />
          <span style={{ width: "100%" }} />
          <span style={{ width: "85%" }} />
          <span style={{ width: "60%" }} />
        </div>
        <span className="doc-grid-thumb-tag">
          {doc.page_count != null ? `${doc.page_count} pages` : "Processing"}
        </span>
      </div>
      <div className="doc-grid-body">
        <div className="doc-grid-title" title={doc.filename}>
          {doc.filename}
        </div>
        <div className="doc-grid-meta">{metaLine(doc)}</div>
        {doc.error_message && <div className="doc-grid-error">{doc.error_message}</div>}
        <div className="doc-grid-foot">
          <StatusBadge status={doc.status} />
          <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
            <button
              className="doc-grid-ask"
              disabled={doc.status !== "ready" || !onAsk}
              onClick={() => onAsk && onAsk(doc.id)}
            >
              Ask AI →
            </button>
          </div>
        </div>
        {doc.status !== "ready" && (
          <button className="ghost-button" onClick={() => onRefresh(doc.id)}>
            Refresh
          </button>
        )}
      </div>
    </article>
  );
}

function EmptyLibrary() {
  return (
    <div className="library-empty">
      <div className="library-empty-icon">
        <FileText size={22} />
      </div>
      <h3>No documents yet</h3>
      <p>Upload your first course PDF to start asking questions grounded in its pages.</p>
    </div>
  );
}
