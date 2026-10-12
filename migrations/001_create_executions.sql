-- Executions are source data from the broker: never edited or rebuilt.
-- Trades are derived from them and can be recreated at any time.
-- Once this file has run on any database, don't edit it; add a new migration.

CREATE TABLE executions (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- The broker's own ID; UNIQUE blocks importing the same execution twice.
    broker_exec_id text UNIQUE NOT NULL,

    executed_at timestamptz NOT NULL,
    ticker text NOT NULL,

    -- Signed: buy > 0, sell < 0. A trade closes when the running sum hits zero,
    -- so numeric (exact decimals) instead of float, which may never reach exactly 0.
    quantity numeric NOT NULL CHECK (quantity <> 0),

    price numeric NOT NULL CHECK (price > 0),

    -- Stored as a positive cost; the importer flips the sign if the broker reports it negative.
    commission numeric NOT NULL CHECK (commission >= 0),

    -- All calculations assume USD. Allowing another currency also requires conversion code.
    currency text NOT NULL CHECK (currency IN ('USD'))
);