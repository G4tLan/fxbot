# Exchange Adapters

[← Back to Supporting Layers Overview](overview.md)

## Overview
The Exchange Adapter layer (`engine/exchanges/`) abstracts the differences between various crypto exchanges, providing a unified interface for the Execution Layer. This allows the same strategy code to run on Binance, Bybit, or a simulated Sandbox environment without modification.

## The `Exchange` Interface
Defined in `engine/exchanges/exchange.py`, this abstract base class mandates the implementation of core trading methods:

- **`market_order`**: Submit a market order.
- **`limit_order`**: Submit a limit order.
- **`stop_order`**: Submit a stop-loss/take-profit order.
- **`cancel_order`**: Cancel a specific order.
- **`cancel_all_orders`**: Cancel all open orders for a symbol.
- **`fetch_precisions`**: Get symbol-specific precision rules (price/quantity decimals).

## The Sandbox Exchange
Located in `engine/exchanges/sandbox/`, this is the default adapter used during **Backtesting** and **Optimization**.
- **Simulation**: It simulates order filling based on historical candle data.
- **Latency**: It assumes zero latency (instant execution) unless configured otherwise.
- **Fees**: It calculates trading fees based on configuration.

## Live Exchanges
(Note: Live exchange drivers are typically loaded dynamically or exist in the `engine-live` plugin). They implement the same `Exchange` interface but communicate with real exchange APIs via HTTP/WebSocket.
