# TASKS.md

## Phase 1: Setup
- [ ] Create the repository structure.
- [ ] Add `CLAUDE.md`, `PROJECT_REQUIREMENTS.md`, `ARCHITECTURE.md`, and `TASKS.md`.
- [ ] Set up environment variables and `.env.example`.
- [ ] Add `.gitignore`.
- [ ] Create the backend and frontend folders.

## Phase 2: Backend Foundation
- [ ] Initialize FastAPI project.
- [ ] Add CORS configuration.
- [ ] Add health check endpoint.
- [ ] Add file upload endpoint.
- [ ] Add basic error handling.
- [ ] Add logging.

## Phase 3: PDF Processing
- [ ] Extract text from uploaded PDFs.
- [ ] Handle multi-page documents.
- [ ] Detect and preserve page numbers.
- [ ] Add fallback handling for scanned or low-quality PDFs.
- [ ] Validate file size and file type.

## Phase 4: Chunking And Embeddings
- [ ] Split extracted text into chunks.
- [ ] Decide chunk size and overlap.
- [ ] Generate embeddings with a multilingual model.
- [ ] Store chunk text and embeddings in Supabase.
- [ ] Save document metadata.

## Phase 5: Retrieval
- [ ] Embed user queries.
- [ ] Run similarity search with pgvector.
- [ ] Return top-k relevant chunks.
- [ ] Add optional filters by document or session.
- [ ] Test retrieval for Tamil, English, and mixed-language queries.

## Phase 6: Answer Generation
- [ ] Build prompt template for grounded answers.
- [ ] Send retrieved context to Ollama.
- [ ] Make the model cite source chunks.
- [ ] Return answer plus supporting references.
- [ ] Handle "not found in document" cases.

## Phase 7: Viva Questions
- [ ] Build viva question prompt.
- [ ] Generate easy, medium, and hard questions.
- [ ] Tie questions to retrieved content.
- [ ] Return formatted viva output.

## Phase 8: Frontend
- [ ] Create upload UI.
- [ ] Create chat UI.
- [ ] Show citations clearly.
- [ ] Add viva question page.
- [ ] Improve layout and responsiveness.

## Phase 9: Evaluation
- [ ] Create test set for Tamil queries.
- [ ] Create test set for English queries.
- [ ] Create test set for mixed-language queries.
- [ ] Measure retrieval quality.
- [ ] Measure citation accuracy.
- [ ] Record failure cases.
- [ ] Compare against a baseline if possible.

## Phase 10: Polish
- [ ] Improve prompts.
- [ ] Tune chunk size and top-k values.
- [ ] Add caching if needed.
- [ ] Improve error messages.
- [ ] Clean up code and documentation.

## Priority Order
1. Backend foundation.
2. PDF processing.
3. Chunking and embeddings.
4. Retrieval.
5. Answer generation.
6. Viva questions.
7. Frontend.
8. Evaluation.
9. Polish.

## Done Criteria
A task is done only when:
- It works end to end.
- It is tested.
- It does not break existing functionality.
- It matches the project requirements.