# Backtest Mode

[← Back to Execution Layer Overview](overview.md)

## Overview
Backtest Mode is the simulation engine of engine. It allows users to test their strategies against historical data to evaluate performance before risking real capital. The entry point is `engine.modes.backtest_mode.run()`.

## The Backtest Lifecycle

### 1. Initialization
- **Configuration**: The user's configuration (routes, exchanges, time range) is loaded.
- **Validation**: Routes are validated to ensure the strategy exists and the exchange is supported.
- **Data Loading**: Historical candles are fetched from the database for the specified time range. If `warmup_candles_num` is set, additional candles before the start date are loaded to prime indicators.

### 2. The Simulation Loop
The core of the backtest is a time-series loop that iterates through the loaded candles.

1.  **Time Step**: The loop advances one candle at a time (based on the smallest timeframe in the routes).
2.  **Price Update**: The current market price (`self.price`) is updated for all traded symbols.
3.  **Order Execution**: The engine checks if any pending orders (Limit/Stop) should be filled based on the new price data.
    - **Slippage**: Can be simulated (though often assumed minimal in basic backtests).
    - **Fees**: Trading fees are deducted from the balance.
4.  **Strategy Update**:
    - `strategy.update_position()` is called if there is an open position.
    - `strategy.should_long()` and `strategy.should_short()` are evaluated to check for new entry signals.
    - `strategy.should_cancel()` is checked to manage pending orders.
5.  **Balance Tracking**: The portfolio value is recalculated at every step to track drawdown and equity.

### 3. Reporting
Once the loop finishes (or is terminated):
- **Metrics Calculation**: Key performance indicators (KPIs) are calculated:
    - Net Profit / ROI
    - Sharpe Ratio, Sortino Ratio, Calmar Ratio
    - Max Drawdown
    - Win Rate
- **Charts**: An equity curve and candle chart (with buy/sell markers) are generated.
- **Logs**: Detailed logs of every trade and order are saved.

## Key Components
- **`engine/modes/backtest_mode.py`**: The main orchestrator.
- **`engine/services/broker.py`**: Handles simulated order placement and balance updates.
- **`engine/store/`**: Holds the in-memory state of the simulation (orders, positions, balance).
