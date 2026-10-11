from fastapi.testclient import TestClient
from app.main import app


def test_health():
    # The server is up. This address does not touch the database.
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == "ok"


def test_health_db():
    # The database is reachable.
    # Needs Postgres running and DATABASE_URL set, from the .env file.
    client = TestClient(app)
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == "ok"


def test_health_db_failure(monkeypatch):
    # Nothing listens on port 5999, so the connection is refused.
    # This simulates the database being down.
    monkeypatch.setenv("DATABASE_URL", "postgresql://postgres@localhost:5999/trading_journal")
    client = TestClient(app)
    response = client.get("/health/db")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database connection error"}


   
    