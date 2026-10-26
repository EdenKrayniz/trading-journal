"""Return a trade's realized profit after commissions, from its exits so far."""


def compute_realized_profit(trade):
    exit_commission = 0
    entry_commission = 0
    exit_quantity = 0
    for link in trade["links"]:
        # Sum from the links what the trades table doesn't store. An exit moves
        # the position toward zero: a sell in a long trade, a buy in a short one.
        if (trade["direction"] == "long" and link["allocated_quantity"] < 0) or (
            trade["direction"] == "short" and link["allocated_quantity"] > 0
        ):
            exit_quantity += abs(link["allocated_quantity"])
            exit_commission += link["allocated_commission"]
        else:
            entry_commission += link["allocated_commission"]
    # No exits yet means nothing is realized. Checked first, because
    # avg_exit_price is None until the first exit.
    if exit_quantity == 0:
        return 0
    elif trade["direction"] == "long":
        price_difference = trade["avg_exit_price"] - trade["avg_entry_price"]
    else:
        price_difference = trade["avg_entry_price"] - trade["avg_exit_price"]
    profit_before_commission = price_difference * exit_quantity
    # Each exit takes a part of the entry commissions in proportion to its size,
    # like the entry price, which also counts only for the shares sold.
    entry_commission_part = (exit_quantity / trade["quantity"]) * entry_commission
    profit = profit_before_commission - entry_commission_part - exit_commission
    return profit
