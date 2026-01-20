# FinderBase

Consumer-friendly “save the web” app:
- Paste a URL -> get clean readable markdown + screenshot
- Your personal searchable library (FTS)

## Stack
- Web: Next.js (Vercel)
- API + Worker: FastAPI + Playwright (Railway)
- DB + Storage + Auth: Supabase

## Setup (Local)
### 1) Supabase
Run SQL in `supabase/migrations/001_init.sql`.

Create Storage bucket: `screenshots` (private).

### 2) API
cd apps/api
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload

### 3) Worker
python -m app.worker

### 4) Web
cd apps/web
cp .env.example .env.local
npm i
npm run dev
