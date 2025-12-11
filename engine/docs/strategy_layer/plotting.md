# Plotting

[← Back to Strategy Layer Overview](overview.md)

## Overview
engine provides a built-in plotting API to visualize custom data on the candle chart. This is extremely useful for debugging strategies and understanding why a trade was taken.

## Methods

### `self.add_line_to_candle_chart(name, value, color)`
Adds a line overlay to the main candle chart.
- **name**: Unique identifier for the line.
- **value**: The y-axis value (e.g., an indicator value).
- **color**: Hex code or color name.

```python
def update_position(self):
    self.add_line_to_candle_chart('EMA 20', self.ema_20, 'blue')
    self.add_line_to_candle_chart('EMA 50', self.ema_50, 'red')
```

### `self.add_extra_line_to_candle_chart(name, value, color)`
Similar to `add_line_to_candle_chart`, but typically used for secondary data.

## Usage in Dashboard
These plots are rendered in the engine Dashboard when viewing backtest results. They allow you to visually inspect the correlation between your indicators and price action.

## Performance Note
Excessive plotting can slow down backtests, especially over long periods. It is recommended to use plotting primarily for debugging or development, and disable it for large-scale optimizations.
