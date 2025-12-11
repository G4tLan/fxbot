# Import Candles Mode

[← Back to Execution Layer Overview](overview.md)

## Overview
Import Candles Mode is responsible for fetching historical OHLCV (Open, High, Low, Close, Volume) data from crypto exchanges and storing it in the local database. This data is the fuel for backtesting and optimization. The entry point is `engine.modes.import_candles_mode.run()`.

## Workflow

### 1. Request
The user specifies:
- **Exchange**: e.g., 'Binance', 'Coinbase'.
- **Symbol**: e.g., 'BTC-USDT'.
- **Start Date**: The beginning of the data range.

### 2. Driver Selection
engine uses a driver-based architecture to support multiple exchanges.
- **`engine/modes/import_candles_mode/drivers/`**: Contains the implementation for each exchange API.
- The system selects the appropriate driver based on the requested exchange.

### 3. Fetching Data
- **Pagination**: Most exchanges limit the number of candles per API call (e.g., 1000 candles). engine calculates the number of batches needed and iterates through them.
- **Rate Limiting**: The downloader respects API rate limits to avoid being banned.
- **Error Handling**: Retries are implemented for network failures or temporary API issues.

### 4. Storage
- **Database**: Data is inserted into the `candle` table in the database (PostgreSQL or SQLite).
- **Deduplication**: Existing candles for the same timestamp are skipped or updated to prevent duplicates.

### 5. Progress Tracking
- The process reports its progress (percentage complete) to the dashboard via Redis/WebSockets so the user can see the status bar.

## Supported Exchanges
engine supports a wide range of exchanges, including:
- Binance (Spot & Futures)
- Bybit
- Coinbase
- Kraken
- FTX (Legacy)
- And many others via the driver interface.
