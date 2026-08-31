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

## Stack

Python, FastAPI, PostgreSQL, React, TypeScript
