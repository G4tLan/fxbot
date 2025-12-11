# Order Management

[← Back to Strategy Layer Overview](overview.md)

## Overview
engine simplifies order management by abstracting the complexity of order types and state tracking. Strategies declare their *intent* (e.g., "I want to buy 1 BTC at $50,000"), and the framework handles the execution.

## Entry Orders
Entry orders are defined in `go_long()` or `go_short()`.

```python
def go_long(self):
    qty = 1.5
    price = self.price
    
    self.buy = qty, price
```

- **Market Order**: If `price` is set to `self.price` (or close to it), it's treated as a Limit order that executes immediately (effectively a Market order in backtests, though technically a Limit).
- **Limit Order**: If `price` is far from the current price, it sits in the order book.

## Exit Orders
Exit orders (Stop-Loss and Take-Profit) are linked to the position.

```python
def go_long(self):
    # ... entry code ...
    
    self.stop_loss = qty, price - 100
    self.take_profit = qty, price + 200
```

- **Stop-Loss**: Triggers a market sell when the price drops to the specified level.
- **Take-Profit**: Places a limit sell order at the specified level.

## Dynamic Updates
You can update orders in `update_position()`:

```python
def update_position(self):
    # Trailing Stop
    if self.price > self.entry_price + 50:
        self.stop_loss = self.position.qty, self.price - 20
```

## Liquidation
To exit a position immediately (Market Sell/Buy):
```python
self.liquidate()
```
