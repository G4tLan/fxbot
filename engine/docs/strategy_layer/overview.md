# Strategy Layer

[← Back to Architecture Overview](../architecture_overview.md)

## Overview
The Strategy Layer is where the user's trading logic resides. It abstracts away the complexities of order management and data handling, providing a clean API for decision-making.

## Components

### [The Strategy Class](strategy_class.md)
The base class for all user strategies. It provides the essential methods, properties, and lifecycle hooks.
- **Key Concept**: Inheritance from `engine.strategies.Strategy`.
- **Data Access**: `self.price`, `self.candles`, `self.position`.

### [Filters & Logic](filters.md)
The decision-making core of your strategy.
- **Entry Triggers**: `should_long()`, `should_short()`.
- **Cancellation**: `should_cancel()`.
- **Modular Logic**: Using `filters()` to combine conditions.

### [Order Management](order_management.md)
How to place and manage trades.
- **Entry**: `go_long()`, `go_short()`.
- **Exit**: Stop-loss, Take-profit, and `liquidate()`.
- **Updates**: Modifying orders in `update_position()`.

### [Indicators](indicators.md)
Using technical analysis tools.
- **Library**: Accessing built-in indicators (`engine.indicators`).
- **Custom**: Creating your own indicators.
- **Performance**: Caching mechanisms.

### [Events](events.md)
Reacting to changes in state.
- **Position Events**: `on_open_position`, `on_close_position`.
- **Route Events**: Reacting to other strategies in the portfolio.

### [Plotting](plotting.md)
Visualizing data for debugging.
- **Charts**: `add_line_to_candle_chart`.
- **Dashboard**: Viewing plots in the UI.
