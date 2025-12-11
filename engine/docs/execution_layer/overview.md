# Execution Layer (Modes)

[← Back to Architecture Overview](../architecture_overview.md)

## Overview
The Execution Layer defines *how* engine runs. Depending on the user's goal, engine switches between different "Modes". Each mode has its own lifecycle and loop, but they all rely on the core infrastructure and strategy layer.

## Components

### 1. [Backtest Mode](backtest_mode.md)
The simulation engine. It loads historical data and replays market movements to evaluate strategy performance.

### 2. [Import Candles Mode](import_mode.md)
The data acquisition engine. It connects to exchanges to download and store historical OHLCV data.

### 3. [Optimization Mode](optimization_mode.md)
The tuning engine. It uses genetic algorithms to find the best combination of hyperparameters for a strategy.

### 4. [Live Mode](live_mode.md)
The real-time trading engine. It connects to live exchange WebSockets to execute trades with real or paper money.

### 5. [The Router](router.md)
The mapping component that assigns strategies to specific exchange-symbol-timeframe combinations, enabling multi-pair trading.
