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


def make_link(execution, allocated_quantity, allocated_commission):
    """Return the link row for the part of an execution that goes to one trade."""
    link = {
        "execution_id": execution["id"],
        "allocated_quantity": allocated_quantity,
        "allocated_commission": allocated_commission,
    }
    return link


def make_trade(execution, quantity, commission):
    """Return a new open trade, starting with this execution's part of it."""
    opened_at = execution["executed_at"]
    if quantity > 0:
        direction = "long"
    else:
        direction = "short"
    link = make_link(execution, quantity, commission)
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
    prices = {}
    for execution in executions:
        # Links hold only the execution id, so prices are kept by id for the totals.
        prices[execution["id"]] = execution["price"]
        if execution["ticker"] != previous_ticker:
            if open_trade is not None:
                trades.append(open_trade)
                open_trade = None
                position = 0
            previous_ticker = execution["ticker"]
        position_before = position
        position_after = position_before + execution["quantity"]
        commission = execution["commission"]
        if position_before == 0:
            open_trade = make_trade(execution, position_after, commission)

        elif position_after == 0:
            open_trade["closed_at"] = execution["executed_at"]
            link = make_link(execution, execution["quantity"], commission)
            open_trade["links"].append(link)
            trades.append(open_trade)
            open_trade = None

        elif (position_before > 0 and position_after < 0) or (
            position_before < 0 and position_after > 0
        ):
            commission_for_closed_trade, commission_for_new_trade = split_commission(
                -position_before, execution["quantity"], commission
            )
            link = make_link(execution, -position_before, commission_for_closed_trade)
            open_trade["closed_at"] = execution["executed_at"]
            open_trade["links"].append(link)
            trades.append(open_trade)
            open_trade = make_trade(execution, position_after, commission_for_new_trade)

        else:
            link = make_link(execution, execution["quantity"], commission)
            open_trade["links"].append(link)
        position = position_after

    # The last ticker's trade may still be open, and no ticker change
    # comes after it to move it to the list.
    if open_trade is not None:
        trades.append(open_trade)
    # Totals are computed once every trade has all its links,
    # including the last open one.
    for trade in trades:
        entry_quantity = 0
        exit_quantity = 0
        total_entry_value = 0
        total_exit_value = 0
        for link in trade["links"]:
            execution_id = link["execution_id"]
            # An entry moves the position away from zero: a buy in a long trade,
            # a sell in a short one. Everything else is an exit.
            if (trade["direction"] == "long" and link["allocated_quantity"] > 0) or (
                trade["direction"] == "short" and link["allocated_quantity"] < 0
            ):
                entry_quantity += abs(link["allocated_quantity"])
                total_entry_value += prices[execution_id] * abs(
                    link["allocated_quantity"]
                )
            else:
                exit_quantity += abs(link["allocated_quantity"])
                total_exit_value += prices[execution_id] * abs(
                    link["allocated_quantity"]
                )
        trade["quantity"] = entry_quantity
        # Not rounded, so quantity times the gap between the averages
        # gives the exact profit.
        trade["avg_entry_price"] = total_entry_value / entry_quantity
        # Exit quantity, not closed_at: a partly sold open trade
        # already has an exit price.
        if exit_quantity != 0:
            trade["avg_exit_price"] = total_exit_value / exit_quantity
        else:
            trade["avg_exit_price"] = None
    return trades
