from engine.models.core import Candle
from engine.store import store
from engine.exchanges.sandbox import Sandbox
from engine.strategies.Strategy import Strategy
import numpy as np
import time

def run_backtest(exchange_name: str, symbol: str, timeframe: str, start_date: str, end_date: str, strategy_class):
    print(f"Starting Backtest for {symbol}...")
    
    # 1. Load Data
    # Convert dates to timestamps
    try:
        start_ts = int(time.mktime(time.strptime(start_date, "%Y-%m-%d"))) * 1000
        end_ts = int(time.mktime(time.strptime(end_date, "%Y-%m-%d"))) * 1000
    except ValueError:
        print("Invalid date format.")
        return

    candles_query = Candle.select().where(
        (Candle.exchange == exchange_name) &
        (Candle.symbol == symbol) &
        (Candle.timestamp >= start_ts) &
        (Candle.timestamp <= end_ts)
    ).order_by(Candle.timestamp)
    
    # Convert to list/numpy for speed
    # [timestamp, open, high, low, close, volume]
    candles_list = []
    for c in candles_query:
        candles_list.append([c.timestamp, float(c.open), float(c.high), float(c.low), float(c.close), float(c.volume)])
    
    if not candles_list:
        print("No candles found for backtest.")
        return

    all_candles = np.array(candles_list)
    print(f"Loaded {len(all_candles)} candles.")

    # 2. Initialize Components
    store.reset()
    store.app_mode = 'backtest'
    store.balance = {'Sandbox': 10000} # Start with 10k
    
    sandbox = Sandbox()
    strategy = strategy_class(symbol, 'Sandbox', timeframe)
    strategy.setUp()

    # 3. Simulation Loop
    # We need at least some candles to calculate indicators (warmup)
    warmup_period = 50 
    
    for i in range(warmup_period, len(all_candles)):
        # Current slice of history
        current_slice = all_candles[:i+1]
        current_candle = all_candles[i]
        
        # Update Store
        store.price = current_candle[4] # Close price
        store.current_candle = current_candle
        
        # Update Strategy
        strategy.candles = current_slice
        
        # Lifecycle: Update Position
        strategy.update_position()
        
        # Lifecycle: Check Signals
        # 1. Long
        if strategy.should_long():
            strategy.go_long()
            
            # Process Intents
            if strategy.buy:
                for order in strategy.buy:
                    qty, price = order
                    # Execute via Sandbox
                    sandbox.market_order(symbol, qty, 'buy')
                # Reset intent
                strategy.buy = []

        # 2. Short (omitted for brevity, similar logic)
        
        # 3. Exits (Stop Loss / Take Profit) - Simplified check
        # In a real engine, we'd check if Low < SL or High > TP
        
    # 4. Results
    strategy.terminate()
    final_balance = store.balance['Sandbox']
    print(f"Backtest Complete.")
    print(f"Initial Balance: 10000")
    print(f"Final Balance: {final_balance:.2f}")
    print(f"PnL: {((final_balance - 10000) / 10000) * 100:.2f}%")

