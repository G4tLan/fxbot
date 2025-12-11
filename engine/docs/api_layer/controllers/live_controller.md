# Live Controller

[← Back to API Layer Overview](../overview.md)

## Purpose
The Live Controller manages live trading and paper trading sessions. It interfaces with the `engine-live` plugin to execute real-time strategies.

## Key Endpoints

### `POST /live`
Starts a new live or paper trading session.
- **Input**: `LiveRequestJson` (exchange, api keys, config, routes)
- **Process**: Spawns a process running `engine_live.live_mode.run`.
- **Requires Auth**: Yes

### `POST /live/cancel`
Stops a running live trading session.
- **Input**: `LiveCancelRequestJson`
- **Requires Auth**: Yes
