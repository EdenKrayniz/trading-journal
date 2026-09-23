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
