from decimal import ROUND_HALF_UP, Decimal


def split_commission(allocated_quantity, quantity, commission):
    """Split an execution's commission between two trades, by share of quantity."""
    first_commission = ((allocated_quantity / quantity) * commission).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    # The remainder, not the same formula, so the two parts always sum to
    # exactly the commission, even after the first part is rounded.
    second_commission = commission - first_commission
    return first_commission, second_commission
