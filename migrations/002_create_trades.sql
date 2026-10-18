-- Trades are derived from executions: they can be deleted and rebuilt at any time.
-- Once this file has run on any database, don't edit it; add a new migration.

-- One row per trade: from a zero position back to zero.
CREATE TABLE trades (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticker text NOT NULL,
    opened_at timestamptz NOT NULL,

    -- NULL while the trade is still open.
    closed_at timestamptz,

    direction text NOT NULL CHECK (direction IN ('long', 'short')),

    -- All shares that entered the position, so quantity times the gap between
    -- the two average prices gives the profit. Unsigned: direction holds the side.
    quantity numeric NOT NULL CHECK (quantity > 0),

    avg_entry_price numeric NOT NULL CHECK (avg_entry_price > 0),

    -- NULL until the first exit; a partly closed trade already has one.
    avg_exit_price numeric CHECK (avg_exit_price > 0),

    -- Equal is allowed: a trade can open and close in the same second.
    -- An open trade passes, because a comparison with NULL never fails a CHECK.
    CHECK (opened_at <= closed_at),

    -- The id changes on every rebuild, so trade notes link through
    -- ticker and opened_at, which come out the same each time.
    UNIQUE (ticker, opened_at)
);

-- Which executions make up each trade. An execution that crosses zero
-- is split between two trades, so each row holds only its allocated part.
CREATE TABLE trade_executions (
    -- A rebuild deletes all trades, and their links go with them.
    trade_id integer NOT NULL REFERENCES trades(id) ON DELETE CASCADE,

    -- No cascade: executions are source data, so deleting one in use is blocked.
    execution_id integer NOT NULL REFERENCES executions(id),

    -- Signed like the execution, so a closed trade's quantities sum to zero.
    allocated_quantity numeric NOT NULL CHECK (allocated_quantity <> 0),

    allocated_commission numeric NOT NULL CHECK (allocated_commission >= 0),

    -- An execution counts once per trade; a duplicate row would count it twice.
    PRIMARY KEY (trade_id, execution_id)
);