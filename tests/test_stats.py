from decimal import Decimal

from app.stats import compute_realized_profit


def test_compute_realized_profit_partial_exit():
    link_1 = {"allocated_quantity": Decimal(10), "allocated_commission": Decimal("2.5")}
    link_2 = {"allocated_quantity": Decimal(-4), "allocated_commission": Decimal(1)}
    links = [link_1, link_2]
    trade = {
        "direction": "long",
        "quantity": Decimal(10),
        "avg_entry_price": Decimal(100),
        "avg_exit_price": Decimal(110),
        "links": links,
    }
    profit = compute_realized_profit(trade)
    assert profit == Decimal(38)


def test_compute_realized_profit_no_exit():
    link = {"allocated_quantity": Decimal(10), "allocated_commission": Decimal("2.5")}
    links = [link]
    trade = {
        "direction": "long",
        "quantity": Decimal(10),
        "avg_entry_price": Decimal(100),
        "avg_exit_price": None,
        "links": links,
    }
    profit = compute_realized_profit(trade)
    assert profit == Decimal(0)


def test_compute_realized_profit_short():
    link_1 = {
        "allocated_quantity": Decimal(-10),
        "allocated_commission": Decimal("2.5"),
    }
    link_2 = {"allocated_quantity": Decimal(4), "allocated_commission": Decimal(1)}
    links = [link_1, link_2]
    trade = {
        "direction": "short",
        "quantity": Decimal(10),
        "avg_entry_price": Decimal(50),
        "avg_exit_price": Decimal(45),
        "links": links,
    }
    profit = compute_realized_profit(trade)
    assert profit == Decimal(18)
