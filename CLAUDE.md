# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Job market insights tool. Scrapes job postings, enriches them with LLM-extracted
structured fields, stores embeddings for similarity search, and surfaces
aggregate insights (top skills, tech stack, seniority) in a Gradio UI.

This is a **two-process app**: a FastAPI backend (port 8000) and a Gradio
frontend (`backend/app.py`) that talks to the backend over HTTP at
`http://localhost:8000`. Both must be running.

## Running

All commands must run from the `backend/` directory — module imports
(`app.*`, `embeddings.*`) and the ChromaDB path (`vector_store`, relative to cwd)
only resolve when cwd is `backend/`.

```bash
cd backend
.\venv\Scripts\activate          # venv lives at backend/venv (Windows)

uvicorn app.main:app --reload    # backend API on :8000
python app.py                    # Gradio frontend (separate terminal), :7860
```

There is no test suite. `backend/test_pw.py` is an ad-hoc Playwright scratch
script, not part of CI. Several modules have `if __name__ == "__main__"` blocks
for manual runs, but some call their entrypoints with no args and will error —
they are not maintained entrypoints.

## Required environment (`.env` at repo root)

`load_dotenv()` is called from the `backend/` cwd and walks up to the repo-root
`.env` (which is gitignored).

- `OPENAI_API_KEY` — used for both LLM extraction and embeddings.
- `JSEARCH_API_KEY` — RapidAPI key for the JSearch job-search API.
- `DATABASE_URL` — async SQLAlchemy URL, e.g.
  `postgresql+asyncpg://postgres:<password>@localhost:5432/job_insights`.

## Architecture & data flow

The scrape pipeline is triggered by `POST /api/scrape?role=...` and runs
synchronously end-to-end:

1. **`app/ingestion/ingest_jobs.py`** → calls `scrape_jsearch` and writes raw
   `JobPosting` rows via `crud.create_job_posting`.
2. **`app/scraping/jsearch_scraper.py`** → fetches postings from the JSearch
   RapidAPI endpoint. (The `fetch_job_details` LinkedIn-scraping helper exists
   but is not wired into the active pipeline.)
3. **`app/llm/process_jobs.py`** → finds rows missing enrichment, calls
   `extract_job_insights` (OpenAI `gpt-4o-mini`, strict-JSON system prompt in
   `app/llm/extractor.py`) to fill `skills_extracted`, `tech_stack`,
   `seniority`, `summary`, then generates an embedding (`text-embedding-3-small`)
   and upserts it into ChromaDB.

`GET /api/insights/overview?role=...` aggregates the enriched fields in Python
(`collections.Counter`) — `skills_extracted`/`tech_stack` are stored as
comma-joined strings and split back apart at query time. The Gradio frontend
renders these as Plotly charts. **Omitting `role` aggregates across every
posting**; the Gradio dropdown's default "All Roles" option (`ALL_ROLES` in
`app.py`) relies on this by calling the endpoint with no `role` param.

`DELETE /api/jobs` deletes postings for a given `role`, or — when `role` is
omitted — **every** posting in the table. The Gradio "All Roles" view keeps the
delete button enabled (delete-all) but disables scraping, which is inherently
role-specific. Note: delete only touches the Postgres table, not ChromaDB.

Similarity search (`GET /api/similar/{job_id}`) re-embeds the stored job and
queries ChromaDB by cosine distance.

### Storage

- **PostgreSQL** holds the relational `job_postings` table (`app/db/models.py`).
  Access is fully async via SQLAlchemy `asyncpg`. The connection string is read
  from the `DATABASE_URL` environment variable (`.env`); `app/db/database.py`
  raises at import if it is unset.
- **ChromaDB** (`backend/vector_store/`, committed to the repo) is a persistent
  local vector store, collection `jobs`, cosine space. Wrapped by
  `embeddings/vector_store.py`.

There is **no migration tooling and no `Base.metadata.create_all`** call — the
Postgres database and `job_postings` table must be provisioned manually before
the backend will work.

## Things that will trip you up

- **Legacy OpenAI SDK** (`openai==0.28.1`): code uses `openai.ChatCompletion.create`
  and `openai.Embedding.create`. Do not upgrade to the 1.x SDK without rewriting
  these call sites.
- **`requirements.txt` is incomplete / inconsistent**: it lists `psycopg2-binary`
  but the code uses `asyncpg`, and omits runtime deps that are installed in the
  venv (fastapi, uvicorn, gradio, sqlalchemy, httpx, beautifulsoup4, plotly,
  python-dotenv). Treat `backend/venv` as the source of truth for what's actually
  installed.
- **CORS** in `app/main.py` still allows `http://localhost:5173` — leftover from
  a removed React frontend; the live UI is Gradio.
- `process_jobs.py` marks jobs with no description as "processed" by setting all
  enrichment fields to empty strings, so they won't be retried.
- **Compiled bytecode and the vector store are committed** (`__pycache__/*.pyc`,
  `backend/vector_store/chroma.sqlite3` and its `*.bin` files), so they show up
  as modified on nearly every run. They are not in `.gitignore`; avoid bundling
  these incidental changes into unrelated commits.
