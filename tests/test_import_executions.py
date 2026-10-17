from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.import_executions import convert_row_to_execution

row = {
    "DateTime": "20240101;123456",
    "IBExecID": "123456789",
    "Symbol": "AAPL",
    "Quantity": "10",
    "TradePrice": "150.00",
    "IBCommission": "-1.00",
    "CurrencyPrimary": "USD",
}


def test_negative_commission_becomes_positive():
    execution = convert_row_to_execution(row)
    assert execution["commission"] == Decimal("1.00")


def test_right_time_winter():
    execution = convert_row_to_execution(row)
    assert execution["executed_at"] == datetime(
        2024, 1, 1, 17, 34, 56, tzinfo=ZoneInfo("UTC")
    )


def test_right_time_summer():
    summer_row = row.copy()
    summer_row["DateTime"] = "20240701;123456"
    execution = convert_row_to_execution(summer_row)
    assert execution["executed_at"] == datetime(
        2024, 7, 1, 16, 34, 56, tzinfo=ZoneInfo("UTC")
    )
