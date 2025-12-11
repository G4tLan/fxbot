# Configuration

[← Back to Core Infrastructure Overview](overview.md)

## Overview
Configuration in engine is centralized and managed via the `engine/config.py` module. It handles settings for exchanges, database connections, logging, and system preferences. The configuration is dynamic and can be adjusted at runtime depending on the execution mode (Backtest, Live, Optimize).

## The `config` Dictionary
The core of the configuration is a global dictionary named `config` in `engine/config.py`. It is divided into two main sections: `env` (user environment settings) and `app` (runtime application state).

### 1. `env` (Environment Settings)
This section contains settings that define the user's trading environment.

#### `caching`
Controls how data is cached.
- **`driver`**: The caching driver to use (default: `'pickle'`).

#### `logging`
Granular control over what events are logged.
- **`strategy_execution`**: Log strategy execution steps.
- **`order_submission`**: Log when orders are submitted.
- **`order_cancellation`**: Log when orders are canceled.
- **`order_execution`**: Log when orders are filled.
- **`position_opened`**: Log when a new position is opened.
- **`position_increased`**: Log when a position size is increased.
- **`position_reduced`**: Log when a position size is reduced.
- **`position_closed`**: Log when a position is closed.
- **`shorter_period_candles`**: Log updates for shorter timeframe candles.
- **`trading_candles`**: Log updates for trading timeframe candles.
- **`balance_update`**: Log balance changes.
- **`exchange_ws_reconnection`**: Log WebSocket reconnection events.

#### `exchanges`
Configuration for each exchange. Keys are exchange names (e.g., 'Binance', 'Sandbox').
- **`fee`**: Trading fee percentage (e.g., `0.001` for 0.1%).
- **`type`**: Exchange type (`'spot'` or `'futures'`).
- **`balance`**: Initial balance for backtesting.
- **`futures_leverage`**: Leverage multiplier (e.g., `1`, `10`).
- **`futures_leverage_mode`**: Margin mode (`'cross'` or `'isolated'`).

#### `optimization`
Settings specific to the optimization mode.
- **`objective_function`**: The metric to optimize for (e.g., `'sharpe'`, `'calmar'`, `'sortino'`).
- **`trials`**: Number of trials per hyperparameter combination.

#### `data`
Settings related to data handling.
- **`warmup_candles_num`**: Number of candles to load before the start date to warm up indicators.
- **`generate_candles_from_1m`**: If `True`, larger timeframes are generated from 1m candles (Live mode).
- **`persistency`**: If `True`, data is persisted to the database (Live mode).

### 2. `app` (Application State)
This section is used internally by engine to track the runtime state. These values are typically populated during the startup process.

- **`considering_symbols`**: List of all symbols involved in the session.
- **`trading_symbols`**: List of symbols actively being traded.
- **`considering_timeframes`**: List of all timeframes involved.
- **`trading_timeframes`**: List of timeframes used for trading decisions.
- **`considering_exchanges`**: List of all exchanges involved.
- **`trading_exchanges`**: List of exchanges where orders are placed.
- **`trading_mode`**: Current mode (`'backtest'`, `'livetrade'`, `'fitness'`).
- **`debug_mode`**: Boolean flag to enable verbose debugging logs.
- **`is_unit_testing`**: Boolean flag indicating if running in a test environment.

## Configuration Management Functions

### `set_config(conf: dict)`
Updates the global `config` dictionary with values provided by the user or the dashboard.
- **Backtest/Live**: Updates logging, exchange settings (fees, balance, leverage), and warmup candles.
- **Optimize**: Updates objective function, trials, and warmup candles.
- **Live Only**: Updates notifications and data persistency settings.

### `reset_config()`
Resets the `config` dictionary to its initial state using a backup copy. Useful for clearing state between unit tests or sessions.

## User Configuration
When running a project, engine loads a `config.py` file from the user's project root. This file allows users to override default settings, such as:
- Adding API keys for exchanges.
- Configuring database connections (PostgreSQL host, port, credentials).
- Setting up notification channels (Telegram, Discord).

The `engine.modes.data_provider.get_config()` function merges the user's local configuration with the system defaults and database-stored options to provide the final configuration object used by the dashboard.
