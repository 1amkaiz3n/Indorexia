-- Indorexia - Supabase Database Schema
-- Jalankan SQL ini di Supabase SQL Editor

create extension if not exists "pgcrypto";

create table if not exists research (
    id uuid primary key default gen_random_uuid(),
    visitor_id text not null default '',
    title text not null default '',
    query text not null,
    location text not null default '',
    verdict text not null default '',
    score int not null default 0,
    pinned bool not null default false,
    raw_data jsonb not null default '{}'::jsonb,
    report jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists research_visitor_idx on research (visitor_id, created_at desc);
create index if not exists research_pinned_idx on research (visitor_id, pinned desc);

alter table research enable row level security;

create policy "Allow all on research"
    on research for all
    using (true)
    with check (true);
