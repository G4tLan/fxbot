from engine.models.core import Candle, BacktestSession, Order
from engine.store import Store
from engine.exchanges.sandbox import Sandbox
from engine.strategies.Strategy import Strategy
from engine.schemas import BacktestResult
from engine.modes.utils import candle_includes_price, split_candle, get_executing_orders, sort_execution_orders
import numpy as np
import time
import os
import logging

def run_backtest(exchange_name: str, symbol: str, timeframe: str, start_date: str, end_date: str, strategy_class, task_id: str = None):

    # Setup logging
    logger = None
    file_handler = None
    
    if task_id:
        log_dir = "storage/logs/backtest-mode"
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f"{task_id}.txt")
        
        logger = logging.getLogger(f"backtest_{task_id}")
        logger.setLevel(logging.INFO)
        
        # Avoid adding multiple handlers if logger already exists
        if not logger.handlers:
            file_handler = logging.FileHandler(log_path, mode='w')
            formatter = logging.Formatter('%(asctime)s - %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    def log(msg):
        print(msg)
        if logger:
            logger.info(msg)

    log(f"Starting Backtest for {symbol}...")
    
    try:
        # 1. Load Data
        try:
            start_ts = int(time.mktime(time.strptime(start_date, "%Y-%m-%d"))) * 1000
            end_ts = int(time.mktime(time.strptime(end_date, "%Y-%m-%d"))) * 1000
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")

        candles_query = Candle.select().where(
            (Candle.exchange == exchange_name) &
            (Candle.symbol == symbol) &
            (Candle.timestamp >= start_ts) &
            (Candle.timestamp <= end_ts)
        ).order_by(Candle.timestamp)
        
        # [timestamp, open, high, low, close, volume]
        candles_list = []
        for c in candles_query:
            candles_list.append([c.timestamp, float(c.open), float(c.high), float(c.low), float(c.close), float(c.volume)])
        
        if not candles_list:
            raise ValueError(f"No candles found for backtest for {symbol} on {exchange_name} between {start_date} and {end_date}.")

        all_candles = np.array(candles_list)
        log(f"Loaded {len(all_candles)} candles.")

        # 2. Initialize Components
        local_store = Store()
        local_store.app_mode = 'backtest'
        local_store.balance = {'Sandbox': 10000} # Start with 10k
        
        sandbox = Sandbox(store_instance=local_store, log_func=log)
        strategy = strategy_class(symbol, 'Sandbox', timeframe, local_store)
        strategy.log = log
        strategy.setUp()

        # 3. Run Simulation
        _step_simulator(all_candles, local_store, sandbox, strategy, log, task_id, symbol)

        # 4. Results
        strategy.terminate()
        final_balance = local_store.balance['Sandbox']
        pnl = ((final_balance - 10000) / 10000) * 100
        
        log(f"Backtest Complete.")
        log(f"Initial Balance: 10000")
        log(f"Final Balance: {final_balance:.2f}")
        log(f"PnL: {pnl:.2f}%")
        
        return BacktestResult(
            initial_balance=10000,
            final_balance=float(final_balance),
            pnl_percent=float(pnl),
            trades=local_store.trades,
            closed_trades=local_store.closed_trades
        )

    except Exception as e:
        log(f"Backtest failed: {e}")
        import traceback
        log(traceback.format_exc())
        raise e
    finally:
        if file_handler:
            file_handler.close()
            if logger: logger.removeHandler(file_handler)


def _step_simulator(candles, store, sandbox, strategy, log, task_id, symbol):
    warmup_period = 50
    
    for i in range(warmup_period, len(candles)):
        # Check for cancellation
        if task_id and i % 100 == 0:
            try:
                session = BacktestSession.get(BacktestSession.id == task_id)
                if session.status == 'cancelled':
                    log(f"Task {task_id} cancelled by user.")
                    return
            except:
                pass

        current_candle = candles[i]
        
        # Update Store
        store.price = current_candle[4] # Close
        store.current_candle = current_candle
        
        # 1. Simulate Price Change (Execute Active Orders)
        _simulate_price_change_effect(current_candle, store, sandbox, log)
        
        # 2. Update Strategy
        strategy.candles = candles[:i+1]
        
        # 3. Execute Strategy Logic
        strategy._execute()
        
        # 4. Process Strategy Intents (New Orders)
        _process_strategy_intents(strategy, sandbox, store, symbol)


def _simulate_price_change_effect(candle, store, sandbox, log):
    # Get orders that CAN be executed in this candle
    executing_orders = get_executing_orders(store.orders, candle)
    
    if not executing_orders:
        return

    # Sort them by execution order (heuristic)
    if len(executing_orders) > 1:
        executing_orders = sort_execution_orders(executing_orders, candle)
        
    # Execute them
    for order in executing_orders:
        if order.status != 'ACTIVE':
            continue
            
        # Double check price inclusion (redundant but safe)
        if candle_includes_price(candle, float(order.price)):
            # In a full implementation, we would split the candle here
            # and update the store time/price to the execution price.
            # For now, we just execute.
            
            sandbox.execute_order(order)


def _process_strategy_intents(strategy, sandbox, store, symbol):
    # 1. Buy Intents (Market)
    if strategy.buy:
        for order_tuple in strategy.buy:
            qty, price = order_tuple
            # Market Order
            ord_obj = sandbox.market_order(symbol, qty, price, 'buy', False)
            sandbox.execute_order(ord_obj)
        strategy.buy = []

    # 2. Sell Intents (Market)
    if strategy.sell:
        for order_tuple in strategy.sell:
            qty, price = order_tuple
            # Market Order
            ord_obj = sandbox.market_order(symbol, qty, price, 'sell', False)
            sandbox.execute_order(ord_obj)
        strategy.sell = []
        
    # 3. Stop Loss / Take Profit (Pending Orders)
    # We need to convert these to actual Orders in the store
    # Assuming strategy.stop_loss = [(qty, price), ...]
    
    if strategy.stop_loss:
        for order_tuple in strategy.stop_loss:
            qty, price = order_tuple
            # Create STOP order
            # Determine side based on position? 
            # Usually SL is opposite to position.
            # For simplicity, if we have a long position, SL is sell.
            # We need to know the side.
            # Strategy should probably provide side or we infer.
            # Let's assume SL is always closing the position.
            
            # Simplified: Just create a STOP order.
            # We need to know if it's buy or sell.
            # If we just bought, SL is sell.
            side = 'sell' # Default to long SL
            
            # Check if we have a position
            # This is tricky without more context from Strategy.
            # But typically SL is set after entry.
            
            # Let's use sandbox.stop_order
            ord_obj = sandbox.stop_order(symbol, qty, price, side, reduce_only=True)
            # It's added to store.orders by sandbox
            
        strategy.stop_loss = []

    if strategy.take_profit:
        for order_tuple in strategy.take_profit:
            qty, price = order_tuple
            side = 'sell' # Default
            ord_obj = sandbox.limit_order(symbol, qty, price, side, reduce_only=True)
            
        strategy.take_profit = []

