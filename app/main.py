import os
import psycopg
from fastapi import FastAPI, HTTPException

app = FastAPI()
@app.get("/health")
def health():
    return "ok"

@app.get("/health/db")
def health_db():
    try:
        with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            conn.execute("SELECT 1;")
            return "ok"
    except psycopg.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection error")
    


