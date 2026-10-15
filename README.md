# trading-journal

Takes an execution report from a broker, reconstructs complete trades from it, and computes statistics and discipline rules over them.

## Design

Source data is separated from derived data.

- Executions come from the broker and are never modified
- Trades are derived, and can be deleted and rebuilt
- Trade notes are my own manual input and are never deleted

A trade runs flat to flat: from zero position until the
position returns to zero. A single execution can be split
across two trades.

Trade notes are linked to trades by the natural key
ticker + opened_at, not by a running ID.
Trades are rebuilt from executions, so a running ID
points to a different trade after every rebuild —
silently, with no error raised.
The natural key is derived from the data itself and
survives the rebuild.

## Stack

Python, FastAPI, PostgreSQL, React, TypeScript

## Database migrations

The schema is managed as numbered SQL files in `migrations/`,
applied by a small runner in `app/migrate.py`. It was written by hand
instead of using Alembic, to understand every step; switch to Alembic
when there are several developers or servers.

- File names: a three-digit number and an imperative description,
  e.g. `001_create_executions.sql`. Files run in name order.
- Once a file has run on any database, never edit it. Every change is a new file.
- Each database records the files it has run in `schema_migrations`,
  so every file runs once per database.
- A run is one transaction: if any file fails, nothing from that run is saved.

Run locally (reads `DATABASE_URL` from `.env`):

```
uv run --env-file .env python -m app.migrate
```

Runs automatically:

- CI: on every push, on an empty throwaway database, before the tests.
- Render: at the end of the build command, on every deploy:

```
uv sync --frozen --no-dev && uv cache prune --ci && uv run --no-dev python -m app.migrate
```
