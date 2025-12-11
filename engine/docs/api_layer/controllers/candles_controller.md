# Candles Controller

[← Back to API Layer Overview](../overview.md)

## Purpose
The Candles Controller manages the importation and management of historical candle data. It allows users to download data from exchanges and clear the local cache.

## Key Endpoints

### `POST /candles/import`
Starts a background process to import candles from an exchange.
- **Input**: `ImportCandlesRequestJson` (exchange, symbol, start_date)
- **Process**: Spawns `engine.modes.import_candles_mode.run`.
- **Requires Auth**: Yes

### `POST /candles/cancel-import`
Cancels a running import process.
- **Input**: `CancelRequestJson` (id)
- **Requires Auth**: Yes

### `POST /candles/clear-cache`
Clears the internal database cache for candles to free up memory or force a reload.
- **Requires Auth**: Yes
