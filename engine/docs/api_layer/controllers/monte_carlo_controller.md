# Monte Carlo Controller

[← Back to API Layer Overview](../overview.md)

## Purpose
The Monte Carlo Controller manages Monte Carlo simulations, which are used to stress-test strategies by randomizing trade sequences or market data.

## Key Endpoints

### `POST /monte-carlo`
Starts a new Monte Carlo simulation.
- **Input**: `MonteCarloRequestJson`
- **Process**: Spawns `engine.modes.monte_carlo_mode.run`.
- **Requires Auth**: Yes

### `POST /monte-carlo/cancel`
Cancels a running simulation.
- **Input**: `CancelMonteCarloRequestJson`
- **Requires Auth**: Yes

### `POST /monte-carlo/get-sessions`
Retrieves past Monte Carlo sessions.
- **Requires Auth**: Yes
