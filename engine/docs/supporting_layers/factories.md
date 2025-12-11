# Factories

[← Back to Supporting Layers Overview](overview.md)

## Overview
Factories (`engine/factories/`) are utility classes used to generate synthetic or "fake" data objects. They are primarily used in **Unit Tests** and the **Sandbox** exchange simulation.

## Key Factories

### `candle_factory`
Generates synthetic candle data.
- **Usage**: Creating deterministic price patterns to test strategy logic (e.g., "create a sequence of candles where price goes up 10%").

### `order_factory`
Generates `Order` objects.
- **Usage**: Simulating order submission and filling without interacting with a real exchange.

## Example
```python
from engine.factories import fake_candle

# Create a fake candle with specific OHLCV
candle = fake_candle(open=100, close=110, high=115, low=95, volume=1000)
```
