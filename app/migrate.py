import os

import psycopg

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    # Created here, not in a migration: the tool must read this table to decide what to run.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            filename text PRIMARY KEY,
            applied_at timestamptz DEFAULT now() NOT NULL
        );
        """
    )
    rows = conn.execute("SELECT filename  FROM schema_migrations;").fetchall()
    already_applied = set()
    for row in rows:
        already_applied.add(row[0])
    print("Already applied migrations:", already_applied)
    names = os.listdir("migrations")
    # os.listdir returns names in arbitrary order, so we sort them ourselves.
    # Zero-padded numbers (001, 002, ...) make string order match run order.
    ordered_names = sorted(names)
    print("Found migrations:", ordered_names)
    print("Connected to the database successfully.")
