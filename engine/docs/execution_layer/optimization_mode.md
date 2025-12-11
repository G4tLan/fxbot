# Optimization Mode

[← Back to Execution Layer Overview](overview.md)

## Overview
Optimization Mode is designed to tune the hyperparameters of a strategy to maximize its performance. Instead of manually guessing values for indicators (e.g., RSI period, Stop-Loss %), users can define a search space, and engine will find the best combination. The entry point is `engine.modes.optimize_mode.run()`.

## How it Works

### 1. Hyperparameter Definition
In the strategy class, users define hyperparameters using the `hyperparameters()` method:
```python
def hyperparameters(self):
    return [
        {'name': 'rsi_period', 'type': 'integer', 'min': 10, 'max': 30, 'default': 14},
        {'name': 'stop_loss', 'type': 'decimal', 'min': 0.01, 'max': 0.05, 'default': 0.02},
    ]
```

### 2. Search Strategy
engine primarily uses **Genetic Algorithms** (via the `Optuna` library or custom implementation) to explore the search space efficiently.
- **Population**: A set of random hyperparameter combinations (DNA).
- **Evolution**: The best-performing combinations are selected to "breed" the next generation, introducing mutations to explore new areas.

### 3. Execution
- **Parallelization**: Optimization is CPU-intensive. engine uses `multiprocessing` to run multiple backtests in parallel, utilizing all available CPU cores.
- **Evaluation**: Each backtest is scored based on a specific objective function (e.g., Sharpe Ratio, Net Profit).

### 4. Results
- **Best DNA**: The combination of parameters that yielded the highest score.
- **Report**: A list of top-performing configurations is saved to the database (`OptimizationSession`).

## Key Components
- **`engine/modes/optimize_mode/Optimize.py`**: The optimizer engine.
- **`engine/modes/optimize_mode/fitness.py`**: Defines the fitness functions (scoring metrics).
