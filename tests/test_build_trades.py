from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.build_trades import build_trades, split_commission


def test_split_commission_even():
    first_commission, second_commission = split_commission(
        Decimal(-10), Decimal(-15), Decimal("1.50")
    )
    assert first_commission == Decimal("1.00")
    assert second_commission == Decimal("0.50")


def test_split_commission_uneven():
    first_commission, second_commission = split_commission(
        Decimal(-1), Decimal(-3), Decimal("2.50")
    )
    assert first_commission == Decimal("0.83")
    assert second_commission == Decimal("1.67")


def test_split_commission_half_rounds_up():
    first_commission, second_commission = split_commission(
        Decimal(1), Decimal(4), Decimal("2.5")
    )
    assert first_commission == Decimal("0.63")
    assert second_commission == Decimal("1.87")


time_1 = datetime(2026, 3, 2, 10, 0, tzinfo=ZoneInfo("America/New_York"))
time_2 = datetime(2026, 3, 2, 11, 0, tzinfo=ZoneInfo("America/New_York"))
time_3 = datetime(2026, 3, 2, 12, 0, tzinfo=ZoneInfo("America/New_York"))
time_4 = datetime(2026, 3, 2, 13, 0, tzinfo=ZoneInfo("America/New_York"))


def test_build_trades_simple_trade():
    executions = [
        {
            "id": 1,
            "ticker": "AAPL",
            "executed_at": time_1,
            "quantity": Decimal(10),
            "commission": Decimal("2.50"),
            "price": Decimal(100),
        },
        {
            "id": 2,
            "ticker": "AAPL",
            "executed_at": time_2,
            "quantity": Decimal(-5),
            "commission": Decimal("2.50"),
            "price": Decimal(110),
        },
        {
            "id": 3,
            "ticker": "AAPL",
            "executed_at": time_3,
            "quantity": Decimal(5),
            "commission": Decimal("2.50"),
            "price": Decimal(104),
        },
        {
            "id": 4,
            "ticker": "AAPL",
            "executed_at": time_4,
            "quantity": Decimal(-10),
            "commission": Decimal("2.50"),
            "price": Decimal(112),
        },
    ]
    trades = build_trades(executions)
    assert len(trades) == 1
    trade = trades[0]
    assert trade["ticker"] == "AAPL"
    assert trade["opened_at"] == time_1
    assert trade["closed_at"] == time_4
    assert trade["direction"] == "long"
    assert trade["quantity"] == Decimal(15)
    assert trade["avg_entry_price"] == Decimal(1520) / Decimal(15)
    assert trade["avg_exit_price"] == Decimal(1670) / Decimal(15)
    expected_links = [
        {
            "execution_id": 1,
            "allocated_quantity": Decimal(10),
            "allocated_commission": Decimal("2.50"),
        },
        {
            "execution_id": 2,
            "allocated_quantity": Decimal(-5),
            "allocated_commission": Decimal("2.50"),
        },
        {
            "execution_id": 3,
            "allocated_quantity": Decimal(5),
            "allocated_commission": Decimal("2.50"),
        },
        {
            "execution_id": 4,
            "allocated_quantity": Decimal(-10),
            "allocated_commission": Decimal("2.50"),
        },
    ]
    assert trade["links"] == expected_links


def test_build_trades_crossing_zero():
    executions = [
        {
            "id": 1,
            "ticker": "AAPL",
            "executed_at": time_1,
            "quantity": Decimal(10),
            "commission": Decimal("2.50"),
            "price": Decimal(110),
        },
        {
            "id": 2,
            "ticker": "AAPL",
            "executed_at": time_2,
            "quantity": Decimal(-15),
            "commission": Decimal("2.50"),
            "price": Decimal(130),
        },
    ]
    trades = build_trades(executions)
    assert len(trades) == 2
    trade_1 = trades[0]
    assert trade_1["ticker"] == "AAPL"
    assert trade_1["opened_at"] == time_1
    assert trade_1["closed_at"] == time_2
    assert trade_1["direction"] == "long"
    assert trade_1["quantity"] == Decimal(10)
    assert trade_1["avg_entry_price"] == Decimal(1100) / Decimal(10)
    assert trade_1["avg_exit_price"] == Decimal(1300) / Decimal(10)
    expected_first_links = [
        {
            "execution_id": 1,
            "allocated_quantity": Decimal(10),
            "allocated_commission": Decimal("2.50"),
        },
        {
            "execution_id": 2,
            "allocated_quantity": Decimal(-10),
            "allocated_commission": Decimal("1.67"),
        },
    ]
    assert trade_1["links"] == expected_first_links
    trade_2 = trades[1]
    assert trade_2["ticker"] == "AAPL"
    assert trade_2["opened_at"] == time_2
    assert trade_2["closed_at"] is None
    assert trade_2["direction"] == "short"
    assert trade_2["quantity"] == Decimal(5)
    assert trade_2["avg_entry_price"] == Decimal(650) / Decimal(5)
    assert trade_2["avg_exit_price"] is None
    expected_second_links = [
        {
            "execution_id": 2,
            "allocated_quantity": Decimal(-5),
            "allocated_commission": Decimal("0.83"),
        }
    ]
    assert trade_2["links"] == expected_second_links


def test_build_trades_ticker_change():
    executions = [
        {
            "id": 1,
            "ticker": "AAPL",
            "executed_at": time_1,
            "quantity": Decimal(10),
            "commission": Decimal("2.50"),
            "price": Decimal(200),
        },
        {
            "id": 2,
            "ticker": "MSFT",
            "executed_at": time_2,
            "quantity": Decimal(5),
            "commission": Decimal("2.50"),
            "price": Decimal(250),
        },
    ]
    trades = build_trades(executions)
    assert len(trades) == 2
    trade_1 = trades[0]
    assert trade_1["ticker"] == "AAPL"
    assert trade_1["opened_at"] == time_1
    assert trade_1["closed_at"] is None
    assert trade_1["direction"] == "long"
    assert trade_1["quantity"] == Decimal(10)
    assert trade_1["avg_entry_price"] == Decimal(200)
    assert trade_1["avg_exit_price"] is None
    expected_first_links = [
        {
            "execution_id": 1,
            "allocated_quantity": Decimal(10),
            "allocated_commission": Decimal("2.50"),
        },
    ]
    assert trade_1["links"] == expected_first_links
    trade_2 = trades[1]
    assert trade_2["ticker"] == "MSFT"
    assert trade_2["opened_at"] == time_2
    assert trade_2["closed_at"] is None
    assert trade_2["direction"] == "long"
    assert trade_2["quantity"] == Decimal(5)
    assert trade_2["avg_entry_price"] == Decimal(250)
    assert trade_2["avg_exit_price"] is None
    expected_second_links = [
        {
            "execution_id": 2,
            "allocated_quantity": Decimal(5),
            "allocated_commission": Decimal("2.50"),
        }
    ]
    assert trade_2["links"] == expected_second_links


def test_build_trades_partial_exit():
    executions = [
        {
            "id": 1,
            "ticker": "AAPL",
            "executed_at": time_1,
            "quantity": Decimal(10),
            "commission": Decimal("2.50"),
            "price": Decimal(100),
        },
        {
            "id": 2,
            "ticker": "AAPL",
            "executed_at": time_2,
            "quantity": Decimal(-4),
            "commission": Decimal("2.50"),
            "price": Decimal(110),
        },
    ]
    trades = build_trades(executions)
    assert len(trades) == 1
    trade = trades[0]
    assert trade["ticker"] == "AAPL"
    assert trade["opened_at"] == time_1
    assert trade["closed_at"] is None
    assert trade["direction"] == "long"
    assert trade["quantity"] == Decimal(10)
    assert trade["avg_entry_price"] == Decimal(100)
    assert trade["avg_exit_price"] == Decimal(110)
    expected_links = [
        {
            "execution_id": 1,
            "allocated_quantity": Decimal(10),
            "allocated_commission": Decimal("2.50"),
        },
        {
            "execution_id": 2,
            "allocated_quantity": Decimal(-4),
            "allocated_commission": Decimal("2.50"),
        },
    ]
    assert trade["links"] == expected_links
