# Backtest Controller

[← Back to API Layer Overview](../overview.md)

## Purpose
The Backtest Controller is responsible for managing backtesting sessions. It allows users to start new backtests, stop running ones, and retrieve information about past sessions.

## Key Endpoints

### `POST /backtest`
Initiates a new backtest process.
- **Input**: `BacktestRequestJson` (config, routes, time range, etc.)
- **Process**: Spawns a new process via `process_manager` to run `engine.modes.backtest_mode.run`.
- **Requires Auth**: Yes

### `POST /backtest/cancel`
Cancels a running backtest.
- **Input**: `CancelRequestJson` (id)
- **Requires Auth**: Yes

### `POST /backtest/get-sessions`
Retrieves a list of previous backtest sessions.
- **Requires Auth**: Yes
