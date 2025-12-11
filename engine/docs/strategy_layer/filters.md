# Filters

[← Back to Strategy Layer Overview](overview.md)

## Overview
Filters are boolean methods that you implement within your **Strategy Class**. They act as the gatekeepers for your trading logic, determining *if* an action (like entering a trade or canceling an order) should be taken.

All of these methods must be defined inside your custom strategy class (inheriting from `Strategy`).

## Implementation Context

Here is where these methods fit within your strategy file:

```python
from engine.strategies import Strategy

class MyStrategy(Strategy):
    def should_long(self) -> bool:
        # Return True to enter a long position
        return self.rsi < 30 and self.price > self.ema_200

    def should_short(self) -> bool:
        # Return True to enter a short position
        return self.rsi > 70 and self.price < self.ema_200

    def should_cancel(self) -> bool:
        # Return True to cancel pending orders
        return True

    def filters(self):
        # Optional: Return a list of additional checks
        return [self.filter_trend, self.filter_volatility]
```

## `should_long()` / `should_short()`
These are the primary entry triggers. The framework calls them on every new candle.
- **Input**: None (uses `self` state like `self.candles`, `self.indicators`).
- **Output**: `bool` (Return `True` to signal an entry).
- **Logic**: Combine your indicator conditions here.

```python
def should_long(self):
    # Example: Enter long if RSI is oversold AND price is above 200 EMA
    return self.rsi < 30 and self.price > self.ema_200
```

## `should_cancel()`
Determines if pending entry orders should be canceled. This is checked on every candle *after* an order has been submitted but *before* it is filled.
- **Usage**: If the market moves away from your limit order, or the setup is no longer valid.

```python
def should_cancel(self):
    # Example: Cancel if the order has been open for more than 5 candles
    return len(self.orders) > 0 and (self.time - self.orders[0].created_at) > 5 * 60 * 1000
```

## `filters()`
A list of additional filter functions that must *all* return `True` for an entry to happen. This is useful for modularizing complex logic (e.g., separating trend checks from volatility checks).

```python
def filters(self):
    return [
        self.filter_trend,
        self.filter_volatility
    ]

def filter_trend(self):
    # Custom logic
    return self.adx > 25

def filter_volatility(self):
    # Custom logic
    return self.atr > 10
```
