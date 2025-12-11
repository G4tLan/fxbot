# Research Tools

[← Back to Supporting Layers Overview](overview.md)

## Overview
The Research module (`engine/research/`) exposes engine's core capabilities as a library for use in **Jupyter Notebooks** or custom Python scripts. This is essential for quantitative analysts who want to explore data or prototype strategies without running the full application.

## Key Functions

### Data Access
- **`get_candles(exchange, symbol, timeframe, start_date, end_date)`**: Retrieves historical candle data from the database as a NumPy array.
- **`store_candles(candles, exchange, symbol, timeframe)`**: Manually saves candles to the database.

### Simulation
- **`backtest(config, routes, extra_routes, candles)`**: Runs a backtest programmatically. Returns a dictionary of metrics and charts.
- **`import_candles(exchange, symbol, start_date)`**: Triggers the candle import process.

### Monte Carlo
- **`monte_carlo_trades(trades)`**: Runs Monte Carlo simulation on a list of closed trades to estimate risk.

## Usage Example
```python
from engine.research import get_candles, backtest

# 1. Get Data
candles = get_candles('Binance', 'BTC-USDT', '4h', '2023-01-01', '2024-01-01')

# 2. Define Route
routes = [{'exchange': 'Binance', 'symbol': 'BTC-USDT', 'timeframe': '4h', 'strategy': 'MyStrategy'}]

# 3. Run Backtest
result = backtest(config, routes, [], {'Binance-BTC-USDT': {'4h': candles}})
print(result['metrics'])
```
