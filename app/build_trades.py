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


def make_link(execution, allocated_quantity):
    """Return the link row for the part of an execution that goes to one trade."""
    link = {"execution_id": execution["id"], "allocated_quantity": allocated_quantity}
    return link


def make_trade(execution, quantity):
    """Return a new open trade, starting with this execution's part of it."""
    opened_at = execution["executed_at"]
    if quantity > 0:
        direction = "long"
    else:
        direction = "short"
    link = make_link(execution, quantity)
    links = [link]
    trade = {
        "ticker": execution["ticker"],
        "opened_at": opened_at,
        "closed_at": None,
        "direction": direction,
        "links": links,
    }
    return trade


def build_trades(executions):
    """Build trades from executions sorted by ticker, then time."""
    trades = []
    open_trade = None
    position = 0
    previous_ticker = None
    for execution in executions:
        if execution["ticker"] != previous_ticker:
            if open_trade is not None:
                trades.append(open_trade)
                open_trade = None
                position = 0
            previous_ticker = execution["ticker"]
        position_before = position
        position_after = position_before + execution["quantity"]
        if position_before == 0:
            open_trade = make_trade(execution, position_after)

        elif position_after == 0:
            open_trade["closed_at"] = execution["executed_at"]
            link = make_link(execution, execution["quantity"])
            open_trade["links"].append(link)
            trades.append(open_trade)
            open_trade = None

        elif (position_before > 0 and position_after < 0) or (
            position_before < 0 and position_after > 0
        ):
            link = make_link(execution, -position_before)
            open_trade["closed_at"] = execution["executed_at"]
            open_trade["links"].append(link)
            trades.append(open_trade)
            open_trade = make_trade(execution, position_after)

        else:
            link = make_link(execution, execution["quantity"])
            open_trade["links"].append(link)
        position = position_after

    # The last ticker's trade may still be open, and no ticker change
    # comes after it to move it to the list.
    if open_trade is not None:
        trades.append(open_trade)
    return trades
