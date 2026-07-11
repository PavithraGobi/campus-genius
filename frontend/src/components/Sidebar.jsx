import { Upload, MessagesSquare, Search, Library, Settings, GraduationCap, HelpCircle } from "lucide-react";

// Order matches the real product flow: get a document in, ask about it,
// inspect retrieval, generate viva questions from it, manage the shelf,
// tune preferences.
const TABS = [
  { id: "upload", label: "Upload", icon: Upload },
  { id: "ask", label: "Ask AI", icon: MessagesSquare },
  { id: "search", label: "Search", icon: Search },
  { id: "viva", label: "Viva", icon: HelpCircle },
  { id: "library", label: "Library", icon: Library },
  { id: "settings", label: "Settings", icon: Settings },
];

export default function Sidebar({ active, onChange, readyCount = 0, totalCount = 0 }) {
  // Each tab's count is grounded in the same document state the panels
  // use - not a decorative number. Library shows the whole shelf; Ask
  // and Search show only what's actually queryable right now.
  const countFor = (id) => {
    if (id === "library") return totalCount;
    if (id === "ask" || id === "search" || id === "viva") return readyCount;
    return null;
  };

  return (
    <nav className="sidebar">
      <div className="sidebar-brand">
        <span className="sidebar-brand-mark" aria-hidden="true">
          <GraduationCap size={18} strokeWidth={2} />
        </span>
        <div>
          <div className="sidebar-brand-title">Campus Genius</div>
          <div className="sidebar-brand-sub">Grounded Course Q&amp;A</div>
        </div>
      </div>

      <div>
        <div className="sidebar-eyebrow">Workspace</div>
        <ul className="sidebar-tabs">
          {TABS.map((tab) => {
            const count = countFor(tab.id);
            const Icon = tab.icon;
            return (
              <li key={tab.id}>
                <button
                  className={`sidebar-tab ${active === tab.id ? "is-active" : ""}`}
                  onClick={() => onChange(tab.id)}
                  aria-current={active === tab.id ? "page" : undefined}
                >
                  <span className="sidebar-tab-icon" aria-hidden="true">
                    <Icon size={17} strokeWidth={2} />
                  </span>
                  <span className="sidebar-tab-label">{tab.label}</span>
                  {count > 0 && <span className="sidebar-tab-count">{count}</span>}
                </button>
              </li>
            );
          })}
        </ul>
      </div>

      <div className="sidebar-foot">
        <span className="sidebar-foot-dot" aria-hidden="true" />
        Campus Genius
      </div>
    </nav>
  );
}
