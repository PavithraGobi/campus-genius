# Campus Genius — frontend

React + Vite frontend for the Campus Genius FastAPI backend (Phase 6).

## Setup

```bash
cd frontend
npm install
cp .env.example .env   # edit VITE_API_BASE_URL if the backend isn't on :8000
npm run dev
```

Then run the backend separately (`uvicorn main:app --reload` from `backend/`).
The backend's default CORS allow-list covers `http://localhost:5173` and
`http://localhost:3000`, which is where Vite serves this app by default.

## Pages

- **Library** — upload a PDF (`POST /documents/upload`), see its processing
  status, and refresh individual documents (`GET /documents/{id}`). The
  backend has no "list all documents" endpoint, so the browser remembers
  which document ids it has uploaded (localStorage) and polls each one
  until it leaves `pending`/`processing`.
- **Ask** — grounded Q&A (`POST /answer/ask`). Shows the generated answer,
  an `insufficient_context` warning banner when the backend couldn't find
  strong enough matches, and the cited source chunks.
- **Search** — raw retrieval only (`POST /retrieval/search`), for
  inspecting chunk ranking without going through answer generation.

## Notes on the backend contract

Every field rendered in the UI maps directly to a field on
`DocumentResponse`, `AnswerResponse`, or `RetrievedChunk` in
`backend/app/models/`. No endpoints were added, renamed, or assumed beyond
`/health`, `/documents/upload`, `/documents/{id}`, `/retrieval/search`, and
`/answer/ask`. No backend files were modified.
