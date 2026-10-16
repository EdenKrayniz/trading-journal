"""Import stock executions from an Interactive Brokers Flex Query CSV file.

Run from the project root, with the path of the downloaded report at the end:
    uv run --env-file .env python -m app.import_executions <path-to-csv>
"""

import csv
import os
import sys
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import psycopg

# The connection block is one transaction: if any row fails, nothing from
# this file is saved, so after a fix the whole file can simply be run again.
with psycopg.connect(os.environ["DATABASE_URL"]) as conn, open(sys.argv[1], "r") as f:
    reader = csv.DictReader(f)
    change_counter = 0
    for row in reader:
        # CASH rows are currency conversions (USD.ILS), not stock trades.
        if row["AssetClass"] == "STK":
            # The broker reports New York local time. A named zone, not a fixed
            # -04:00, so winter executions get -05:00 automatically.
            time = datetime.strptime(row["DateTime"], "%Y%m%d;%H%M%S")
            executed_at = time.replace(tzinfo=ZoneInfo("America/New_York"))
            broker_exec_id = row["IBExecID"]
            ticker = row["Symbol"]
            # Decimal straight from the text, never through float, to stay exact.
            quantity = Decimal(row["Quantity"])
            price = Decimal(row["TradePrice"])
            # Reported as negative; the table stores commission as a positive cost.
            commission = -Decimal(row["IBCommission"])
            currency = row["CurrencyPrimary"]
            # Each report covers the last 365 days and repeats imported rows,
            # so existing executions are skipped instead of failing the file.
            changes = conn.execute(
                """
                INSERT INTO executions (
                    executed_at,
                    broker_exec_id,
                    ticker,
                    quantity,
                    price,
                    commission,
                    currency
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (broker_exec_id) DO NOTHING;
                """,
                (
                    executed_at,
                    broker_exec_id,
                    ticker,
                    quantity,
                    price,
                    commission,
                    currency,
                ),
            )
            change_counter += changes.rowcount

# Printed after the block, because rows are saved only when it ends.
print(f"Imported {change_counter} new executions.")
