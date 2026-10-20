from decimal import Decimal

from app.build_trades import split_commission


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
