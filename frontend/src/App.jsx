import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import StatusStrip from "./components/StatusStrip.jsx";
import UploadPanel from "./components/UploadPanel.jsx";
import LibraryPanel from "./components/LibraryPanel.jsx";
import AskPanel from "./components/AskPanel.jsx";
import SearchPanel from "./components/SearchPanel.jsx";
import VivaPanel from "./components/VivaPanel.jsx";
import SettingsPanel from "./components/SettingsPanel.jsx";
import { getHealth } from "./api/client.js";
import { useDocumentLibrary } from "./hooks/useDocumentLibrary.js";
import { getStoredTheme, applyTheme } from "./lib/preferences.js";

export default function App() {
  const [tab, setTab] = useState("upload");
  const [health, setHealth] = useState("checking");
  const [lastUpload, setLastUpload] = useState(null);
  const [askDocumentId, setAskDocumentId] = useState("");
  const { documents, addDocument, refresh } = useDocumentLibrary();

  useEffect(() => {
    applyTheme(getStoredTheme());
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function check() {
      try {
        await getHealth();
        if (!cancelled) setHealth("ok");
      } catch {
        if (!cancelled) setHealth("error");
      }
    }
    check();
    const timer = setInterval(check, 15000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  function goAskWithDocument(id) {
    setAskDocumentId(id);
    setTab("ask");
  }

  function handleUploaded(doc) {
    addDocument(doc);
    setLastUpload({ filename: doc.filename, uploadedAt: doc.created_at });
  }

  const readyCount = documents.filter((d) => d.status === "ready").length;

  return (
    <div className="app-shell">
      <Sidebar
        active={tab}
        onChange={setTab}
        readyCount={readyCount}
        totalCount={documents.length}
      />
      <main className="app-main">
        <StatusStrip health={health} documents={documents} lastUpload={lastUpload} />
        {tab === "upload" && (
          <UploadPanel
            documents={documents}
            onUploaded={handleUploaded}
            onAsk={goAskWithDocument}
            onOpenLibrary={() => setTab("library")}
          />
        )}
        <div style={{ display: tab === "ask" ? "block" : "none" }}>
          <AskPanel documents={documents} presetDocumentId={askDocumentId} />
        </div>
        {tab === "search" && <SearchPanel documents={documents} />}
        {tab === "viva" && <VivaPanel documents={documents} />}
        {tab === "library" && (
          <LibraryPanel documents={documents} onRefresh={refresh} onAsk={goAskWithDocument} />
        )}
        {tab === "settings" && <SettingsPanel />}
      </main>
    </div>
  );
}
