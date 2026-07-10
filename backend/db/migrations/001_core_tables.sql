-- Campus Genius — Phase 1 core tables: documents, chunks
-- Run this against your Supabase project (SQL Editor, or via CLI migration).

-- ============================================
-- Extensions
-- ============================================
create extension if not exists vector;
create extension if not exists pgcrypto; -- for gen_random_uuid()

-- ============================================
-- documents
-- ============================================
create table documents (
    id              uuid primary key default gen_random_uuid(),
    filename        text not null,
    file_path       text not null,
    upload_time     timestamptz not null default now(),
    language_hint   text,                    -- e.g. 'ta', 'en', 'mixed'
    status          text not null default 'pending'
                        check (status in ('pending', 'processing', 'ready', 'failed')),
    page_count      integer,
    file_size_bytes bigint,
    error_message   text,                    -- populated if status = 'failed'
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now()
);

create index idx_documents_status on documents (status);

-- ============================================
-- chunks
-- Embedding dimension is 1024 for the current BAAI/bge-m3 dense output
-- according to the published model spec. If the embedding model changes,
-- this column and index must be recreated to match the new output size.
-- ============================================
create table chunks (
    id            uuid primary key default gen_random_uuid(),
    document_id   uuid not null references documents(id) on delete cascade,
    chunk_index   integer not null,
    chunk_text    text not null,
    embedding     vector(1024),
    page_number   integer,
    token_count   integer,
    created_at    timestamptz not null default now(),

    unique (document_id, chunk_index)
);

-- Vector similarity index (IVFFlat; suitable for small/demo-scale data)
create index idx_chunks_embedding on chunks
    using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);

create index idx_chunks_document_id on chunks (document_id);

-- ============================================
-- Row Level Security
-- No policies are defined — this blocks all access via the anon/authenticated
-- keys (e.g. from a frontend). The backend uses SUPABASE_SERVICE_ROLE_KEY,
-- which bypasses RLS entirely, so this has no effect on the FastAPI service.
-- Revisit this when/if the frontend ever talks to Supabase directly.
-- ============================================
alter table documents enable row level security;
alter table chunks enable row level security;

-- ============================================
-- updated_at trigger for documents
-- ============================================
create or replace function set_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger trg_documents_updated_at
before update on documents
for each row execute function set_updated_at();
