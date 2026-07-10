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

## Future Work
- Authentication.
- Chat history.
- OCR for scanned PDFs.
- Better ranking and reranking.
- UI polish.
- Evaluation dashboard.

## License
Add a license before publishing the project publicly.