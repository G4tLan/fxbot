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
- **Phase 3: Data Acquisition** (Pending) 🚧
- **Phase 4: Simulation Engine** (Pending) 🚧
- **Phase 5: API Layer** (Pending) 🚧

## Setup

1.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Initialize Database**:
    ```bash
    python init_db.py
    ```
    This creates `db.sqlite3` with the required schema.

## Running Tests

To run the test suite, execute the following from the project root (`/home/g4tlan/apps/fxbot`):

```bash
engine/.venv/bin/python -m unittest discover engine/tests
```

## Directory Structure

- `models/`: Database definitions (Candle, Order, Trade, etc.)
- `strategies/`: Base Strategy class and user strategies.
- `indicators/`: Technical analysis indicators (RSI, SMA, EMA).
- `services/`: Core services (Cache, etc.).
- `tests/`: Unit tests for the engine.
- `docs/`: Detailed architecture and implementation documentation.
