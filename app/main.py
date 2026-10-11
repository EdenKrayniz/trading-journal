import os

import psycopg
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/health")
def health():
    # Does not touch the database, so it works even when Postgres is down.
    return "ok"


@app.get("/health/db")
def health_db():
    try:
        with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            # Connecting is not enough; a query proves the server really answers.
            conn.execute("SELECT 1;")
            return "ok"
    # Only connection failures become 503; other bugs should not be hidden.
    except psycopg.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection error")
