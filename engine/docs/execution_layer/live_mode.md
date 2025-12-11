# Live Mode

[← Back to Execution Layer Overview](overview.md)

## Overview
Live Mode is the real-time execution engine. It connects to crypto exchanges via WebSockets and REST APIs to trade with real money (or paper money).

> **Note**: The core logic for live trading is often contained in the `engine-live` plugin, but it integrates tightly with the main engine framework.

## Key Differences from Backtest

### 1. Real-Time Event Loop
Instead of iterating through a fixed array of historical candles, Live Mode runs an event loop that reacts to incoming data:
- **WebSocket Stream**: Subscribes to trade/ticker channels to get real-time price updates.
- **Order Updates**: Listens for order status changes (Filled, Canceled) from the exchange.

### 2. Order Submission
- **API Keys**: Uses the encrypted API keys stored in the database (`ExchangeApiKeys`).
- **Latency**: Accounts for network delay.
- **Error Handling**: Must handle API errors (e.g., "Insufficient Balance", "System Overload") gracefully without crashing.

### 3. Persistence
- **Database**: Trades and orders are saved to the database immediately.
- **Recovery**: If the bot crashes and restarts, it attempts to restore the state (open positions, active orders) from the database and the exchange.

### 4. Notifications
- Sends real-time alerts (Telegram, Discord) when orders are filled or errors occur.

## Paper Trading
A variation of Live Mode where:
- **Data**: Real-time market data is used.
- **Execution**: Orders are simulated locally (like in backtesting) instead of being sent to the exchange.
- **Usage**: Validating that a strategy works in real-time conditions without financial risk.
