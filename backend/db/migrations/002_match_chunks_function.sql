-- Campus Genius — Phase 5: vector similarity search function
-- Run this against your Supabase project (SQL Editor, or via CLI migration),
-- after 001_core_tables.sql.
--
-- supabase-py's query builder (PostgREST) can't express "order by vector
-- distance" directly, so similarity search is done via an RPC function
-- instead — the standard approach for pgvector + Supabase.

create or replace function match_chunks(
    query_embedding vector(1024),
    match_count int default 5,
    filter_document_id uuid default null
)
returns table (
    id uuid,
    document_id uuid,
    chunk_index int,
    chunk_text text,
    page_number int,
    similarity float
)
language sql
stable
as $$
    select
        c.id,
        c.document_id,
        c.chunk_index,
        c.chunk_text,
        c.page_number,
        1 - (c.embedding <=> query_embedding) as similarity
    from chunks c
    where c.embedding is not null
      and (filter_document_id is null or c.document_id = filter_document_id)
    order by c.embedding <=> query_embedding
    limit match_count;
$$;

-- Note: this function runs with the caller's privileges (default, not
-- SECURITY DEFINER). The backend always calls it via the service-role key,
-- which bypasses RLS anyway, so this has no effect on the FastAPI service.
