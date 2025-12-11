# The Strategy Class

[← Back to Strategy Layer Overview](overview.md)

## Overview
The `Strategy` class (`engine/strategies/Strategy.py`) is the base class for all user-defined strategies. It provides the API for accessing market data, managing orders, and defining trading logic.

## Properties

### Market Data
- **`self.price`**: The current close price of the candle.
- **`self.candles`**: A NumPy array of historical candles (Open, High, Low, Close, Volume).
- **`self.time`**: The timestamp of the current candle.
- **`self.symbol`**: The symbol being traded (e.g., 'BTC-USDT').
- **`self.exchange`**: The exchange name (e.g., 'Binance').
- **`self.timeframe`**: The timeframe of the strategy (e.g., '4h').

### Position Data
- **`self.position`**: The `Position` object representing the current open position.
    - `self.position.qty`: Current size (positive for Long, negative for Short).
    - `self.position.entry_price`: Average entry price.
    - `self.position.pnl`: Unrealized Profit/Loss.
- **`self.balance`**: The current available balance in the wallet.
- **`self.portfolio_value`**: Total value of the portfolio (balance + unrealized PnL).

### Order Management
These properties are used to define your trading intent. You assign values to them inside `go_long()` or `go_short()`, and the framework handles the order submission.

- **`self.buy`**: Set this to place a buy order.
    - **Format**: `(quantity, price)` or a list of tuples `[(qty1, price1), (qty2, price2)]`.
    - **Example**: `self.buy = 1.5, 50000` (Buy 1.5 units at $50,000).
- **`self.sell`**: Set this to place a sell order.
    - **Format**: `(quantity, price)` or a list of tuples.
    - **Example**: `self.sell = 1.5, 50000` (Sell 1.5 units at $50,000).
- **`self.stop_loss`**: Set this to define the stop-loss exit.
    - **Format**: `(quantity, price)` or a list of tuples.
    - **Example**: `self.stop_loss = 1.5, 49000` (Stop out 1.5 units if price hits $49,000).
- **`self.take_profit`**: Set this to define the take-profit exit.
    - **Format**: `(quantity, price)` or a list of tuples.
    - **Example**: `self.take_profit = 1.5, 55000` (Take profit on 1.5 units at $55,000).
- **`self.orders`**: A list of all orders (active, filled, canceled) associated with the current trade lifecycle. Useful for auditing the state of your orders.

## Lifecycle Methods
These methods are called by the execution engine at specific points in the loop.

### `should_long() -> bool`
Called on every candle. Return `True` to signal a Long entry.

### `should_short() -> bool`
Called on every candle. Return `True` to signal a Short entry.

### `go_long()`
Called if `should_long()` returns `True`. Define entry order, stop-loss, and take-profit here.

### `go_short()`
Called if `should_short()` returns `True`. Define entry order, stop-loss, and take-profit here.

### `update_position()`
Called on every candle *if* there is an open position. Use this to adjust stop-loss (trailing stop) or exit early.

### `should_cancel() -> bool`
Called on every candle. Return `True` to cancel pending entry orders.

### `terminate()`
Called at the end of the session. Useful for cleanup or logging final stats.
