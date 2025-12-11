# Implementation Plan

## Phase 1: Core Infrastructure & Data Models
*Goal: Establish the database schema and configuration management using SQLite as the initial storage engine.*

1.  **Project Scaffolding**: Create the directory structure (`engine/`, `engine/models`, `engine/controllers`, etc.) matching the architecture docs.
2.  **Database Setup (Peewee ORM with SQLite)**:
    *   Implement `engine/models.py`.
    *   **SQLite Configuration**: Configure Peewee to use `sqlite:///db.sqlite3` as the default database.
    *   **Data Types**: Use `DecimalField` for all price and volume fields to ensure financial precision.
    *   **Time Handling**: Store all timestamps as UTC integers (Unix timestamps) to avoid timezone issues.
    *   Define the `Candle` model (critical for backtesting).
    *   Define `Order`, `Trade`, and `ClosedTrade` models to track simulation results.
    *   Define `BacktestSession` to store the results of a run.
3.  **Configuration Manager**:
    *   Create a `config.py` module to handle global settings.
    *   Ensure default config points to the local SQLite database.
4.  **In-Memory Store**:
    *   Implement a `store` module (likely a singleton or global state manager) to hold the *current* state of the simulation (current price, open orders, account balance) during a backtest run.

## Phase 2: The Strategy Layer (The "API" for Users)
*Goal: Create the class that users will inherit from. This defines the "language" of the bot.*

1.  **Base Strategy Class**:
    *   Create `engine/strategies/Strategy.py`.
    *   Implement lifecycle methods: `setUp`, `update_position`, `terminate`.
    *   Implement trading methods: `buy`, `sell`, `stop_loss`, `take_profit`.
    *   Implement property accessors: `self.price`, `self.balance`, `self.position`.
    *   *Note: Strategy methods will remain synchronous to keep user logic simple.*
2.  **Indicator Library**:
    *   Create `engine/indicators/`.
    *   Implement indicators using **NumPy/Pandas** directly (instead of wrapping TA-Lib) to ensure easy installation and portability.
    *   Expose standard indicators (RSI, EMA, SMA) in a clean way (e.g., `ta.rsi(self.candles)`).

## Phase 3: Data Acquisition & Exchange Adapters
*Goal: Get historical data into the database so we have something to test against, utilizing the Exchange Adapter pattern.*

1.  **Exchange Adapter Interface**:
    *   Define a base `ExchangeAdapter` class (as per `supporting_layers/exchange_adapters.md`) with methods like `fetch_ohlcv`.
2.  **Binance Adapter Implementation**:
    *   Implement one concrete adapter (e.g., Binance) using `ccxt` or `requests` to fetch historical candles.
3.  **Import Logic**:
    *   Implement `engine/modes/import_candles_mode.py`.
    *   Write the logic to chunk requests (e.g., fetch 1000 candles at a time), handle rate limits, and bulk insert them into the SQLite `Candle` table.

## Phase 4: The Simulation Engine (Backtest Mode)
*Goal: The core loop that replays history.*

1.  **The Router**:
    *   Implement `engine/routes.py` logic to map a (Exchange, Symbol, Timeframe) tuple to a specific `Strategy` class.
2.  **The Broker (Sandbox Adapter)**:
    *   Create `engine/services/broker.py` or `engine/adapters/sandbox.py`.
    *   Implement the "Sandbox" exchange adapter mentioned in supporting layers to simulate order execution.
    *   Logic: "If I buy at Market, deduct fees and update `store.orders`."
3.  **The Backtest Loop**:
    *   Implement `engine/modes/backtest_mode.py`.
    *   **Load**: Fetch all required candles from SQLite into memory (NumPy arrays for speed).
    *   **Loop**: Iterate through candles one by one.
        *   Update `store.current_candle` and `store.price`.
        *   **Prevent Look-Ahead Bias**: Ensure the strategy only receives `candles[:-1]` (closed candles). The current candle should only expose `Open` price (or simulated ticks) to prevent "peeking" at the future Close.
        *   Check `Broker` for order fills (Limit/Stop orders).
        *   Call `strategy.update_position()` or `strategy.should_long()`.
    *   **Calculate**: At the end of the loop, generate metrics (Sharpe Ratio, Max Drawdown, Total Profit).

## Phase 5: API Layer (The Controller)
*Goal: Provide a way to trigger these actions programmatically.*

1.  **FastAPI Setup**:
    *   Initialize the app in `engine/__init__.py`.
2.  **Controllers**:
    *   `ImportController`: Endpoint to trigger the Import Mode background task.
    *   `BacktestController`: Endpoint to receive a config (routes, dates), run the `BacktestMode`, and return the JSON results.
