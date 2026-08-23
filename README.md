# Campus Genius

Campus Genius is a Tamil-English multilingual RAG assistant for college students. It lets users upload academic PDFs, ask questions in Tamil, English, or mixed language, and get grounded answers with citations. It can also generate viva questions from the uploaded content.

## Features
- Upload PDF documents.
- Extract and chunk text from PDFs.
- Store embeddings in Supabase with pgvector.
- Ask questions in Tamil, English, or mixed language.
- Get answers grounded in retrieved document chunks.
- Show citations for source support.
- Generate viva questions from document content.

## Recent Improvements

Verified via baseline (decomposition disabled) vs. fixed comparison on an 18-question eval set:

- **Compound question handling** — questions with multiple parts (e.g. "difference between X and Y, and what is Z") are now correctly decomposed and answered, instead of returning "Insufficient context."
- **Tanglish compound detection** — added Tanglish-specific question-word signals so romanized Tamil-English compound questions trigger decomposition correctly.
- **Answer length** — raised max output tokens from 250 to 600 to stop mid-sentence truncation.
- **Language matching** — added an explicit system prompt rule so answers stay in the question's language (fixes an earlier bug where Tanglish queries returned Chinese output).

See [EVALUATION.md](EVALUATION.md) for the full test methodology and known limitations.

## Tech Stack
- Frontend: React
- Backend: FastAPI
- Database: Supabase Postgres
- Vector search: pgvector
- Local LLM: Ollama
- Embeddings: multilingual model with Tamil support

## Project Structure
```txt
.
├── CLAUDE.md
├── PROJECT_REQUIREMENTS.md
├── ARCHITECTURE.md
├── TASKS.md
├── EVALUATION.md
├── README.md
├── backend/
└── frontend/
```

## How It Works
1. User uploads a PDF.
2. The backend extracts and chunks the text.
3. Chunks are embedded and stored in Supabase.
4. When the user asks a question, the query is embedded.
5. Relevant chunks are retrieved from the vector database.
6. Ollama generates a grounded answer using the retrieved context.
7. The app returns the answer with citations.
8. The app can also generate viva questions from the same context.

## Setup
### Backend
1. Create a virtual environment.
2. Install dependencies.
3. Set environment variables.
4. Run the FastAPI server.

### Frontend
1. Install dependencies.
2. Configure the backend URL.
3. Start the React app.

## Environment Variables
Create a `.env` file with values such as:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `OLLAMA_BASE_URL`
- `EMBEDDING_MODEL`
- `LLM_MODEL`

## Development Notes
- Keep answers grounded in retrieved context.
- Use the same embedding model for indexing and query embedding.
- Keep Tamil and mixed-language support as a core requirement.
- Do not expand scope without updating the project docs.

## Evaluation
Use the evaluation file to test:
- Tamil queries
- English queries
- Mixed-language queries
- Retrieval accuracy
- Citation accuracy
- Viva question quality

## What's Been Tested

The following has been verified with real test runs (see `EVALUATION.md`
for the full methodology):

- PDF upload, chunking, and embedding — verified working
- Retrieval accuracy — consistently strong across Tamil, English, and
  Tanglish queries, including correctly ranking true-negative (unrelated)
  queries lowest
- Grounded answer generation — verified correct and citation-backed for
  single-fact queries in Tamil, English, and Tanglish
- Out-of-scope fallback (`insufficient_context`) — verified correctly
  triggers and returns no fabricated sources
- Viva question generation — verified working across multiple uploaded
  documents, with correct page citations
- Frontend (Upload, Ask, Search, Viva, Library tabs) — verified working
  in-browser, including a fixed chat-history-loss bug on tab switching

## Known Limitations

- **Compound question handling**: questions that combine multiple
  sub-topics, where the source document names but does not define one of
  them, can produce an incorrect or over-cautious answer from the local
  LLM. See [`TEST3_LIMITATION.md`](./TEST3_LIMITATION.md) for full
  details, root cause analysis, and a recommended fix.
- **Local model latency**: generation runs on a CPU-only local model
  (~5-6 tokens/sec), so answers to longer or compound questions can take
  20-40+ seconds. Mitigated with output-length capping and keeping the
  model warm between requests, but not eliminated.

## Future Work
- Authentication.
- Chat history.
- OCR for scanned PDFs.
- Better ranking and reranking.
- UI polish.
- Evaluation dashboard.

## License
Add a license before publishing the project publicly.
