# Supporting Layers

[← Back to Architecture Overview](../architecture_overview.md)

## Overview
While the four main layers (API, Execution, Strategy, Core Infra) form the backbone of engine, there are several supporting layers that provide specialized functionality.

## Components

### [Exchange Adapters](exchange_adapters.md)
The abstraction layer that handles interactions with crypto exchanges.
- **Role**: Standardizes API calls (orders, balance, ticker) across different exchanges.
- **Sandbox**: A simulated exchange implementation for backtesting.

### [Research Tools](research_tools.md)
A collection of utilities designed for use in Jupyter Notebooks or standalone scripts.
- **Role**: Allows quantitative analysis, data manipulation, and programmatic backtesting outside the main application loop.
- **Key Functions**: `get_candles`, `backtest`, `import_candles`.

### [Factories](factories.md)
Utilities for generating synthetic data.
- **Role**: Used primarily in testing and simulation to create fake candles, orders, and trades.
