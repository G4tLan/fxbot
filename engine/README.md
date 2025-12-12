# FXBot Engine

A Python-based algorithmic trading engine designed for backtesting, live trading, and strategy optimization.

## Project Status
- **Phase 1: Core Infrastructure** (Completed) ✅
  - Database models (Peewee/SQLite)
  - Configuration management
  - In-memory store
- **Phase 2: Strategy Layer** (Completed) ✅
  - Base Strategy class
  - Indicator library (NumPy-based)
  - Signal generation logic
- **Phase 3: Data Acquisition** (Completed) ✅
  - Exchange Adapter Interface
  - Binance Driver (using `requests`)
  - Import Mode (Bulk insert to SQLite)
- **Phase 4: Simulation Engine** (Completed) ✅
  - Router (Strategy mapping)
  - Sandbox Exchange (Order simulation)
  - Backtest Mode (Event loop)
- **Phase 5: API Layer** (Completed) ✅
  - FastAPI Server (`engine/main.py`)
  - Import Controller (`/api/v1/import`)
  - Backtest Controller (`/api/v1/backtest`)

## Quick Start

### 1. Setup Environment
```bash
cd engine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python init_db.py
```

### 3. Run the API Server
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`.

## API Usage Examples

### Import Historical Data
Fetch candles from Binance and store them in the local database.
```bash
curl -X POST "http://localhost:8000/api/v1/import" \
     -H "Content-Type: application/json" \
     -d '{
           "exchange": "Binance",
           "symbol": "BTC-USDT",
           "start_date": "2023-01-01"
         }'
```

### Run Backtest
Run a simulation using the imported data.
```bash
curl -X POST "http://localhost:8000/api/v1/backtest" \
     -H "Content-Type: application/json" \
     -d '{
           "exchange": "Sandbox",
           "symbol": "BTC-USDT",
           "timeframe": "1h",
           "start_date": "2023-01-01",
           "end_date": "2023-02-01",
           "strategy_name": "SimpleStrategy"
         }'
```

## Creating a New Strategy

1. Create a new file in `engine/strategies/` (e.g., `my_strategy.py`).
2. Inherit from `Strategy` and implement `should_long` / `go_long`.

```python
from engine.strategies.Strategy import Strategy
import engine.indicators as ta

class MyStrategy(Strategy):
    def should_long(self):
        # Example: Buy if RSI < 30
        rsi = ta.rsi(self.candles, period=14)
        if len(rsi) > 0 and rsi[-1] < 30:
            return True
        return False

    def go_long(self):
        # Place a buy order for 1.0 unit at current price
        self.buy = (1.0, self.price)
```

3. Register your strategy in `engine/controllers/backtest_controller.py` (in the `STRATEGIES` dict) to make it available via API.

## Running Tests

To run the full test suite (Phases 1-5):

```bash
# From the project root (/home/g4tlan/apps/fxbot)
engine/.venv/bin/python -m unittest discover engine/tests
```

## Directory Structure

- `models/`: Database definitions (Candle, Order, Trade, etc.)
- `strategies/`: Base Strategy class and user strategies.
- `indicators/`: Technical analysis indicators (RSI, SMA, EMA).
- `exchanges/`: Adapters for Binance and Sandbox.
- `modes/`: Execution logic for Import and Backtest.
- `controllers/`: FastAPI route handlers.
- `services/`: Core services (Cache, etc.).
- `tests/`: Unit tests for the engine.

## Database Inspection

You can use [Datasette](https://datasette.io/) to explore the SQLite database interactively in your browser.

1. Install Datasette:
   ```bash
   pip install datasette
   ```

2. Run Datasette on your database file:
   ```bash
   datasette db.sqlite3
   ```

3. Open your browser at `http://localhost:8001` to view tables, run SQL queries, and visualize data.

