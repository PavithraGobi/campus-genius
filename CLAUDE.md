# CLAUDE.md

## Project
Campus Genius is a Tamil-English multilingual RAG assistant for college PDFs, notices, notes, syllabus files, and viva support.

## Goal
Build a responsive web app that lets users:
- upload PDFs
- ask questions in Tamil, English, or mixed language
- get grounded answers with citations
- generate viva questions from document content

## Tech Stack
- Frontend: React
- Backend: FastAPI
- Database and vector search: Supabase + pgvector
- Local LLM: Ollama
- Embeddings: multilingual model with Tamil support

## Working Rules
- Follow the scope in `PROJECT_REQUIREMENTS.md`.
- Do not expand scope without permission.
- Make small, focused changes.
- Edit only the files requested.
- Keep code simple and readable.
- Prefer working features over overengineering.
- Use the same embedding model for document indexing and query embedding.
- Ground all answers in retrieved document context.
- Preserve citations where possible.

## Claude Workflow
1. Read the relevant project docs first.
2. Work on one task or one file at a time.
3. If something is unclear, ask before coding.
4. After each change, summarize what changed briefly.
5. Do not change unrelated files.

## Project Priority
1. Backend setup
2. PDF ingestion
3. Embeddings and retrieval
4. Answer generation
5. Citations
6. Viva question generation
7. Frontend UI
8. Evaluation

## Output Style
When responding:
- Be concise.
- Be specific.
- Give practical code or steps.
- Avoid unnecessary explanation.
- If code is requested, return only the requested file(s) and a short summary.

## Important Notes
- Use Supabase for storage and pgvector search.
- Use Ollama for local generation.
- Keep Tamil and mixed-language support as a first-class requirement.
- Treat evaluation as part of the project, not an afterthought.

## Success Criteria
The project is successful if it can:
- ingest PDFs reliably
- answer questions in Tamil and English
- return source-grounded answers
- show citations
- generate viva questions
- perform reasonably on bilingual retrieval tests