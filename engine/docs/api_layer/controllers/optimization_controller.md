# Optimization Controller

[← Back to API Layer Overview](../overview.md)

## Purpose
The Optimization Controller manages the strategy optimization process. It allows users to find the best hyperparameters for their strategies using genetic algorithms or other methods.

## Key Endpoints

### `POST /optimization`
Starts a new optimization session.
- **Input**: `OptimizationRequestJson` (strategy, range, cpu cores, etc.)
- **Process**: Spawns `engine.modes.optimize_mode.run`.
- **Requires Auth**: Yes

### `POST /optimization/cancel`
Cancels a running optimization.
- **Input**: `CancelRequestJson`
- **Requires Auth**: Yes

### `POST /optimization/get-sessions`
Retrieves past optimization sessions.
- **Requires Auth**: Yes
