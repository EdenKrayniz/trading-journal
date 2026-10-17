from decimal import Decimal

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


def test_convert_row_to_execution():
    execution = convert_row_to_execution(row)
    assert execution["commission"] == Decimal("1.00")
