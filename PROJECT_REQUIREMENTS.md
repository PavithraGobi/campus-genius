# PROJECT_REQUIREMENTS.md

## Project Name
Campus Genius

## Project Summary
Campus Genius is a Tamil-English multilingual AI assistant for college students. It helps users upload academic PDFs such as syllabus documents, notices, notes, and project files, then ask questions in Tamil, English, or mixed language. The system returns grounded answers with citations and can also generate viva questions from the uploaded content.

## Problem Statement
College students often search through multiple PDFs, notices, and notes to find simple answers. Existing AI tools are often English-first, less focused on local academic use cases, and may depend on paid APIs. This project aims to provide a free or low-cost bilingual assistant that works better for Tamil-English academic content.

## Project Goals
- Build a working RAG assistant for academic documents.
- Support Tamil, English, and mixed-language queries.
- Store and retrieve document chunks using Supabase and pgvector.
- Generate answers using a local LLM through Ollama.
- Return grounded answers with citations.
- Generate viva questions from document content.
- Evaluate bilingual retrieval quality.

## Core Features
1. PDF upload.
2. Document text extraction.
3. Chunking and preprocessing.
4. Embedding generation.
5. Vector storage in Supabase.
6. Semantic retrieval for user questions.
7. Answer generation with citations.
8. Viva question generation.
9. Tamil, English, and Tanglish support.

## Non-Goals
The first version will not include:
- Mobile app support.
- Voice input or voice output.
- Paid API integrations.
- Complex multi-agent workflows.
- Enterprise-grade admin panels.
- Large-scale user management.

## Technical Stack
- Frontend: React
- Backend: FastAPI
- Database: Supabase Postgres
- Vector search: pgvector
- Local LLM: Ollama
- Embeddings: multilingual model with Tamil support
- File processing: PDF parsing library

## Scope
### Must Have
- Upload and process PDFs.
- Extract and chunk text.
- Store embeddings in Supabase.
- Retrieve relevant chunks for each query.
- Generate grounded answers.
- Show citations.
- Support Tamil, English, and mixed-language queries.
- Generate viva questions.

### Optional If Time Permits
- Authentication.
- Chat history.
- Role-based access.
- Better UI polish.
- Evaluation dashboard.

## Constraints
- Keep the project low-cost or free.
- Prefer local inference where possible.
- Keep the backend easy to explain in viva.
- Use the same embedding model for indexing and query time.
- Do not overcomplicate the first version.

## Success Criteria
The project is successful if it can:
- Ingest PDFs reliably.
- Answer Tamil and English queries.
- Show source-grounded answers.
- Return citations.
- Generate viva questions.
- Perform reasonably well on bilingual evaluation tests.

## Evaluation Criteria
Test the system on:
- Tamil-only queries.
- English-only queries.
- Mixed-language queries.
- Retrieval accuracy.
- Answer correctness.
- Citation accuracy.
- Failure cases.

If possible, compare bilingual retrieval against an English-only baseline.

## Deliverables
- Working backend.
- Working frontend.
- Planning and architecture docs.
- Evaluation dataset.
- Demo-ready final project.
- Final report content.

## Priority Order
1. Project docs.
2. Backend skeleton.
3. PDF ingestion.
4. Retrieval pipeline.
5. Answer generation.
6. Citations.
7. Viva questions.
8. Frontend.
9. Evaluation and polishing.

## Expected Outcome
A practical, demo-ready AI assistant that helps college students query academic documents in Tamil and English with grounded answers and citations.