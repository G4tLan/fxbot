# The Router

[← Back to Execution Layer Overview](overview.md)

## Overview
The Router (`engine/routes/`) is a central component that maps **Trading Routes** to **Strategies**. It allows engine to manage multiple trading pairs and strategies within a single execution session.

## Concept: The Route
A "Route" defines a single trading instance. It consists of:
1.  **Exchange**: Where to trade (e.g., 'Binance').
2.  **Symbol**: What to trade (e.g., 'BTC-USDT').
3.  **Timeframe**: The main interval for the strategy (e.g., '4h').
4.  **Strategy Class**: The Python class that contains the logic (e.g., `MyTrendFollowingStrategy`).

## Configuration
Routes are typically defined in the user's `routes.py` file:

```python
routes = [
    ('Binance', 'BTC-USDT', '4h', 'TrendStrategy'),
    ('Binance', 'ETH-USDT', '1h', 'ScalpingStrategy'),
]
```

## Functionality

### 1. Multi-Strategy Support
The Router allows engine to run different strategies on different pairs simultaneously.
- **Isolation**: Each route has its own instance of the strategy class.
- **Shared State**: They share the same global balance (unless configured otherwise), allowing for portfolio-level management.

### 2. Data Routing
The Router ensures that the correct market data is delivered to the correct strategy instance.
- **Main Candle**: The candle matching the route's timeframe.
- **Extra Candles**: Strategies can request data for other timeframes or symbols (e.g., checking BTC price while trading ETH). The Router manages these dependencies.

### 3. Execution Mapping
When the execution engine runs:
1.  It iterates through all configured routes.
2.  It initializes the corresponding strategy objects.
3.  In the main loop, it calls the lifecycle methods (`update_position`, `should_long`, etc.) for *each* route sequentially.
