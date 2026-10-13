"""Apply pending SQL migrations to the database in DATABASE_URL.

Run from the project root, so the relative "migrations" path resolves:
    uv run --env-file .env python -m app.migrate
"""

import os

import psycopg

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    # Make sure the tool's own table of applied migrations exists.
    # Created here, not in a migration: the tool must read this table to decide what to run.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            filename text PRIMARY KEY,
            applied_at timestamptz DEFAULT now() NOT NULL
        );
        """
    )

    # Collect the names of migrations this database has already run.
    rows = conn.execute("SELECT filename FROM schema_migrations;").fetchall()
    already_applied = set()
    for row in rows:
        already_applied.add(row[0])
    print("Already applied migrations:", already_applied)

    # List the migration files on disk, in run order.
    names = os.listdir("migrations")
    # os.listdir returns names in arbitrary order, so we sort them ourselves.
    # Zero-padded numbers (001, 002, ...) make string order match run order.
    ordered_names = sorted(names)
    # Only .sql files are migrations; macOS may add others (e.g. .DS_Store)
    # that would crash the tool when sent to the database.
    ordered_names_sql = []
    for name in ordered_names:
        if name.endswith(".sql"):
            ordered_names_sql.append(name)
    print("Found migrations:", ordered_names_sql)

    # Go through the migrations this database hasn't run yet.
    for name in ordered_names_sql:
        if name not in already_applied:
            print("Applying migration:", name)
            # os.listdir gives bare names; the path must include the folder.
            with open(os.path.join("migrations", name)) as f:
                text = f.read()
            conn.execute(text)
            conn.execute(
                "INSERT INTO schema_migrations (filename) VALUES (%s);", (name,)
            )
