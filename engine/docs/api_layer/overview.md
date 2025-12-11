# API & Interface Layer

[← Back to Architecture Overview](../architecture_overview.md)

## Overview
The API Layer is the bridge between the engine backend and the outside world (primarily the Vue.js Dashboard). It is built using **FastAPI**, providing a robust and asynchronous web server.

## Key Components

### 1. Entry Point (`engine/__init__.py`)
This file initializes the FastAPI application. It sets up:
- **HTTP Routes**: Endpoints for commands like `/auth`, `/backtest`, `/get-config`.
- **WebSockets**: The `/ws` endpoint used for streaming real-time logs, chart data, and progress updates to the dashboard.
- **Startup/Shutdown Events**: Handling resource initialization and cleanup.

### 2. Controllers (`engine/controllers/`)
Controllers contain the business logic for handling API requests. They validate inputs and trigger the appropriate background tasks.

- **[Auth Controller](controllers/auth_controller.md)**: Handles authentication and token management.
- **[Backtest Controller](controllers/backtest_controller.md)**: Manages backtest sessions.
- **[Candles Controller](controllers/candles_controller.md)**: Handles candle data operations.
- **[Config Controller](controllers/config_controller.md)**: Manages system configuration.
- **[Exchange Controller](controllers/exchange_controller.md)**: Handles exchange-related operations.
- **[File Controller](controllers/file_controller.md)**: Manages file operations (logs, exports).
- **[Live Controller](controllers/live_controller.md)**: Manages live trading sessions.
- **[LSP Controller](controllers/lsp_controller.md)**: Language Server Protocol support (for editor integration).
- **[Monte Carlo Controller](controllers/monte_carlo_controller.md)**: Handles Monte Carlo simulations.
- **[Notification Controller](controllers/notification_controller.md)**: Manages notifications.
- **[Optimization Controller](controllers/optimization_controller.md)**: Manages optimization sessions.
- **[Strategy Controller](controllers/strategy_controller.md)**: Manages strategy files and generation.
- **[System Controller](controllers/system_controller.md)**: System-level operations (info, updates).
- **[Websocket Controller](controllers/websocket_controller.md)**: Handles WebSocket connections.

### 3. Process Management
Since backtests and optimizations can be CPU-intensive, the API layer often delegates these tasks to separate processes to keep the web server responsive.
- **`engine/services/multiprocessing.py`**: A manager that spawns and monitors separate processes for execution modes.

## Communication Pattern
- **REST API**: Used for **Actions** (Start Backtest, Update Config).
- **WebSockets**: Used for **Events** (Progress bar updates, Log messages, Chart updates).
