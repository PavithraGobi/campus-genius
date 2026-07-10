# ARCHITECTURE.md

## System Overview
Campus Genius is a bilingual RAG system for college document search and question answering. The app accepts PDFs, extracts text, chunks and embeds the content, stores vectors in Supabase, retrieves relevant chunks for user questions, and generates grounded answers through Ollama.

## High-Level Flow
1. User uploads a PDF.
2. Backend extracts text from the file.
3. Text is cleaned and split into chunks.
4. Chunks are embedded using a multilingual embedding model.
5. Embeddings and metadata are stored in Supabase with pgvector.
6. User asks a question in Tamil, English, or mixed language.
7. The backend embeds the query and retrieves the most relevant chunks.
8. Retrieved chunks are passed to the local LLM.
9. The model generates an answer with citations.
10. The app optionally generates viva questions from the same context.

## Components
### Frontend
- React UI.
- Upload PDF form.
- Chat interface.
- Result panel with citations.
- Viva question generator view.

### Backend
- FastAPI service.
- File upload endpoint.
- Text extraction and preprocessing pipeline.
- Embedding generation service.
- Retrieval endpoint.
- Answer generation endpoint.
- Viva question endpoint.

### Database
- Supabase Postgres.
- `documents` table for file metadata.
- `chunks` table for chunk text and embeddings.
- Optional `chat_sessions` table for history.
- Optional `users` table if authentication is added later.

### AI Layer
- Ollama for local LLM inference.
- Multilingual embedding model for Tamil and English.
- Prompt templates for answer generation and viva question generation.

## Data Model
### documents
- id
- filename
- file_path
- upload_time
- language_hint
- status

### chunks
- id
- document_id
- chunk_index
- chunk_text
- embedding
- page_number
- created_at

### chat_sessions
- id
- user_id
- title
- created_at

### chat_messages
- id
- session_id
- role
- content
- created_at

## Retrieval Design
- Use the same embedding model for both indexing and query embedding.
- Retrieve top-k chunks by vector similarity.
- Optionally add metadata filters such as document id or page number.
- Prefer short, relevant chunks over very large chunks.
- Keep retrieved context within the LLM token budget.

## Prompt Design
The answer prompt should:
- Use only retrieved context.
- Avoid hallucinations.
- Cite document chunks or page references where possible.
- Say when the answer is not found in the document.
- Support Tamil, English, and mixed-language responses.

The viva prompt should:
- Generate likely exam questions.
- Focus on key concepts from the retrieved content.
- Produce a mix of easy, medium, and hard questions.

## Security And Reliability
- Validate uploaded file types.
- Limit file size.
- Store secrets in environment variables only.
- Do not expose raw database credentials in frontend code.
- Handle parsing failures gracefully.
- Log errors clearly for debugging.

## Performance Considerations
- Chunk documents before embedding.
- Cache repeated retrievals where possible.
- Keep prompts compact.
- Avoid sending unnecessary context to the model.
- Process large PDFs asynchronously if needed.

## Recommended Build Order
1. Create backend skeleton.
2. Add PDF upload and text extraction.
3. Add chunking and embeddings.
4. Add Supabase vector storage.
5. Add retrieval and answer generation.
6. Add citations.
7. Add viva question generation.
8. Build frontend.
9. Add evaluation and testing.

## Future Extensions
- Authentication and access control.
- Chat history.
- Document permissions.
- Better ranking methods.
- OCR for scanned PDFs.
- Admin dashboard.
- Usage analytics.

## Architecture Principles
- Keep the system modular.
- Separate ingestion from retrieval.
- Keep prompts and retrieval logic easy to inspect.
- Make every answer traceable to source text.
- Prefer simple, testable services over tightly coupled code.