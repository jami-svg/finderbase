-- Extensions
create extension if not exists pgcrypto;
create extension if not exists pg_trgm;

-- Jobs
create table if not exists public.scrape_jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  url text not null,
  status text not null default 'queued', -- queued|running|done|failed
  error text,
  created_at timestamptz not null default now(),
  started_at timestamptz,
  finished_at timestamptz
);

create index if not exists scrape_jobs_user_created_idx
  on public.scrape_jobs (user_id, created_at desc);

create index if not exists scrape_jobs_status_created_idx
  on public.scrape_jobs (status, created_at asc);

-- Pages
create table if not exists public.scraped_pages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  url text not null,
  domain text not null,
  scraped_at timestamptz not null default now(),

  title text,
  summary text,
  markdown text not null,

  company_name text,
  language text,
  status_code int,

  screenshot_path text, -- storage path like screenshots/<user>/<id>.png

  seo jsonb not null default '{}'::jsonb,
  contacts jsonb not null default '{}'::jsonb,
  socials jsonb not null default '{}'::jsonb,

  -- Full-text search
  tsv_content tsvector generated always as (
    setweight(to_tsvector('simple', coalesce(title,'')), 'A') ||
    setweight(to_tsvector('simple', coalesce(domain,'')), 'B') ||
    setweight(to_tsvector('simple', coalesce(markdown,'')), 'C')
  ) stored
);

-- Uniqueness: per-user per-url (optional but recommended)
create unique index if not exists scraped_pages_user_url_uq
  on public.scraped_pages (user_id, url);

create index if not exists scraped_pages_user_scraped_idx
  on public.scraped_pages (user_id, scraped_at desc);

create index if not exists scraped_pages_domain_idx
  on public.scraped_pages (domain);

create index if not exists scraped_pages_tsv_idx
  on public.scraped_pages using gin (tsv_content);

-- RLS
alter table public.scrape_jobs enable row level security;
alter table public.scraped_pages enable row level security;

-- Policies: users only see their own rows
create policy "scrape_jobs_select_own"
  on public.scrape_jobs for select
  using (auth.uid() = user_id);

create policy "scrape_jobs_insert_own"
  on public.scrape_jobs for insert
  with check (auth.uid() = user_id);

create policy "scrape_jobs_update_own"
  on public.scrape_jobs for update
  using (auth.uid() = user_id);

create policy "scraped_pages_select_own"
  on public.scraped_pages for select
  using (auth.uid() = user_id);

create policy "scraped_pages_insert_own"
  on public.scraped_pages for insert
  with check (auth.uid() = user_id);

create policy "scraped_pages_update_own"
  on public.scraped_pages for update
  using (auth.uid() = user_id);
