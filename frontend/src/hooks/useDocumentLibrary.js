import { useCallback, useEffect, useState } from "react";
import { getDocument } from "../api/client.js";

const STORAGE_KEY = "campus-genius:document-ids";

function loadIds() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveIds(ids) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
}

/**
 * Tracks the set of document ids this browser has uploaded, and keeps
 * their latest DocumentResponse in state by polling GET /documents/{id}.
 * This is purely a client-side convenience - the backend has no endpoint
 * that lists documents, so nothing here is a source of truth beyond
 * "documents this browser has seen."
 */
export function useDocumentLibrary() {
  const [documents, setDocuments] = useState({}); // id -> DocumentResponse

  const refresh = useCallback(async (id) => {
    try {
      const doc = await getDocument(id);
      setDocuments((prev) => ({ ...prev, [id]: doc }));
      return doc;
    } catch (err) {
      setDocuments((prev) => ({
        ...prev,
        [id]: prev[id] ? { ...prev[id], error_message: err.message } : undefined,
      }));
      return null;
    }
  }, []);

  const addDocument = useCallback(
    (doc) => {
      const ids = new Set(loadIds());
      ids.add(doc.id);
      saveIds([...ids]);
      setDocuments((prev) => ({ ...prev, [doc.id]: doc }));
    },
    []
  );

  useEffect(() => {
    loadIds().forEach((id) => refresh(id));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Poll any document still pending/processing until it settles.
  useEffect(() => {
    const inFlight = Object.values(documents).filter(
      (d) => d && (d.status === "pending" || d.status === "processing")
    );
    if (inFlight.length === 0) return undefined;
    const timer = setInterval(() => {
      inFlight.forEach((d) => refresh(d.id));
    }, 3000);
    return () => clearInterval(timer);
  }, [documents, refresh]);

  const list = Object.values(documents)
    .filter(Boolean)
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

  return { documents: list, addDocument, refresh };
}
