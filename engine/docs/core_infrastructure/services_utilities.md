# Services & Utilities

[← Back to Core Infrastructure Overview](overview.md)

## Overview
engine includes a set of core services and utility functions that support the higher-level logic. These services handle everything from database connections to complex mathematical calculations.

## Core Services (`engine/services/`)

### `Broker` (`engine/services/broker.py`)
The `Broker` class acts as an abstraction layer for exchange interactions. It unifies the interface for placing orders and fetching balances, whether the system is running in Backtest Mode (simulated execution) or Live Mode (real API calls).
- **Key Methods**:
    - `sell_at_market(qty)`: Places a market sell order.
    - `sell_at(qty, price)`: Places a limit sell order.
    - `buy_at_market(qty)`: Places a market buy order.
    - `buy_at(qty, price)`: Places a limit buy order.
    - `cancel_order(order_id)`: Cancels an active order.

### `Logger` (`engine/services/logger.py`)
A structured logging service that handles writing logs to the database, file system, and broadcasting them via WebSockets to the dashboard.
- **Key Functions**:
    - `info(msg)`: Logs an informational message.
    - `error(msg)`: Logs an error message.
    - `broadcast(msg)`: Sends a message to the frontend via Redis/WebSockets.
- **Storage**: Logs are stored in `storage/logs/{mode}/{session_id}.txt`.

### `Selectors` (`engine/services/selectors.py`)
Helper functions to retrieve specific objects from the global store. This is the primary way to access the current state of the system (prices, positions, orders) from anywhere in the code.
- **Key Functions**:
    - `get_current_price(exchange, symbol)`: Returns the current market price.
    - `get_position(exchange, symbol)`: Returns the `Position` object for a specific pair.
    - `get_orders(exchange, symbol)`: Returns a list of active orders.
    - `get_exchange(name)`: Returns the `Exchange` object.

### `Multiprocessing` (`engine/services/multiprocessing.py`)
Manages background processes. Since Python is single-threaded (mostly), engine spawns separate processes for CPU-intensive tasks like backtesting and optimization to keep the API responsive.
- **Key Classes**:
    - `ProcessManager`: Tracks active worker processes and handles their termination.

### `Database` (`engine/services/db.py`)
Manages the connection to the PostgreSQL or SQLite database using Peewee ORM.
- **Key Methods**:
    - `open_connection()`: Establishes a connection to the DB.
    - `close_connection()`: Closes the connection.

### `Cache` (`engine/services/cache.py`)
A simple caching mechanism using Python's `pickle` module to store intermediate results on disk.
- **Usage**: Used to cache calculated indicators or other expensive operations to speed up subsequent runs.

### `Auth` (`engine/services/auth.py`)
Handles user authentication for the API.
- **Key Functions**:
    - `password_to_token(password)`: Generates a JWT token from a password.
    - `is_valid_token(token)`: Verifies a token.

## Data Services

### `Candle` (`engine/services/candle.py`)
Utilities for manipulating candle data.
- **Key Functions**:
    - `generate_candle_from_one_minutes(...)`: Aggregates 1-minute candles into larger timeframes (e.g., 1m -> 1h).
    - `candle_dict_to_np_array(candle)`: Converts a dictionary candle to a NumPy array for faster processing.

### `Metrics` (`engine/services/metrics.py`)
Calculates performance metrics for backtests and trading sessions.
- **Key Functions**:
    - `candles_info(candles_array)`: Returns metadata about the candle series (duration, start/end time).
    - `routes(routes_arr)`: Formats routing information for reports.

## Communication Services

### `Notifier` (`engine/services/notifier.py`)
Handles sending notifications to external services like Telegram, Discord, and Slack.
- **Key Functions**:
    - `notify(msg)`: Queues a message to be sent to the configured notification channels.
    - `start_notifier_loop()`: Starts a background thread that processes the message queue.

## Helpers (`engine/helpers.py`)
A massive collection of utility functions used throughout the codebase.

### Date & Time
- `arrow_to_timestamp(arrow_time)`: Converts an Arrow object to a millisecond timestamp.
- `timestamp_to_arrow(timestamp)`: Converts a timestamp to an Arrow object.
- `now()`: Returns the current timestamp.

### Math & Numbers
- `normalize(qty, precision)`: Rounds a number to a specific precision.
- `floor_with_precision(num, precision)`: Floors a number to a specific precision.

### String & Formatting
- `generate_unique_id()`: Generates a random UUID.
- `clean_string(text)`: Removes special characters from a string.

### Trading Utilities
- `base_asset(symbol)`: Extracts the base asset from a symbol (e.g., 'BTC' from 'BTC-USDT').
- `quote_asset(symbol)`: Extracts the quote asset (e.g., 'USDT').
- `timeframe_to_one_minutes(timeframe)`: Converts a timeframe string (e.g., '1h') to the number of minutes (60).
