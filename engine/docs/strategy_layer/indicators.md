# Indicators

[← Back to Strategy Layer Overview](overview.md)

## Overview
Indicators are mathematical calculations based on historical price, volume, or open interest.

To ensure high performance and easy installation, engine uses **custom NumPy implementations** and **engine-Rust** (a custom Rust library) instead of relying on problematic dependencies like TA-Lib. This approach avoids binary compilation issues while maintaining the speed required for backtesting.

## Usage
Indicators are accessed via `self.indicators` or by importing the library directly.

```python
import engine.indicators as ta
from engine.services.cache import cached

class MyStrategy(Strategy):
    @property
    @cached
    def ema_short(self):
        return ta.ema(self.candles, period=20)

    @property
    @cached
    def rsi(self):
        return ta.rsi(self.candles, period=14)
```

## Caching & Performance
Trading engines often run event loops (iterative), while indicators are best calculated on arrays (vectorized).
- **Vectorization**: engine calculates indicators on the full NumPy array of candles.
- **Caching**: To prevent re-calculating the same indicator multiple times within the same candle loop, use the `@cached` decorator. This ensures that `self.rsi` is calculated once per candle and the result is stored in memory until the next candle arrives.

## Available Indicators
engine supports over 50+ indicators, including:
- **Trend**: SMA, EMA, WMA, SAR, ADX
- **Momentum**: RSI, Stochastic, MACD, CCI, MOM
- **Volatility**: ATR, Bollinger Bands, Keltner Channels
- **Volume**: OBV, AD, MFI

## Custom Indicators
Users can define custom indicators by creating a Python function that accepts a NumPy array of candles and returns a value or array. Since engine uses standard NumPy arrays, you can easily write performant custom logic without needing C/Rust.

```python
def my_custom_indicator(candles):
    closes = candles[:, 2]
    return (closes[-1] + closes[-2]) / 2
```
