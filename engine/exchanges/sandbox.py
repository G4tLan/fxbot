from engine.exchanges.exchange import Exchange
from engine.models.core import Order, Trade
import uuid
import time

class Sandbox(Exchange):
    def __init__(self, store_instance):
        super().__init__('Sandbox')
        self.fee_rate = 0.001 # 0.1%
        self.store = store_instance

    def fetch_ohlcv(self, symbol, timeframe, start_ts, end_ts=None):
        # Sandbox doesn't fetch data, it consumes what's given or mocks it
        return []

    def process_order(self, symbol: str, qty: float, price: float, side: str, type: str):
        """
        Simulate order processing.
        In backtest, this is called instantly.
        """
        # 1. Create Order Record
        order_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000) # In backtest, this should be the current candle time
        
        # For simplicity in this phase, we assume instant fill for Market orders
        # and we don't track Limit orders in a complex orderbook yet.
        
        status = 'EXECUTED'
        executed_at = timestamp
        
        # 2. Update Store (Balance & Position)
        # Key: Exchange-Symbol
        key = f"{self.name}-{symbol}"
        
        # Initialize if not exists
        if key not in self.store.positions:
            self.store.positions[key] = {'qty': 0, 'entry_price': 0}
        
        position = self.store.positions[key]
        current_qty = position['qty']
        current_entry = position['entry_price']
        
        cost = qty * price
        fee = cost * self.fee_rate
        
        # Update Balance (Simplified: assuming single currency USDT)
        # store.balance is a dict {Exchange: Balance}
        if self.name not in self.store.balance:
            self.store.balance[self.name] = 10000 # Default starting balance
            
        if side == 'buy':
            self.store.balance[self.name] -= (cost + fee)
            
            # Update Average Entry Price
            new_qty = current_qty + qty
            if new_qty > 0:
                new_entry = ((current_qty * current_entry) + (qty * price)) / new_qty
                position['entry_price'] = new_entry
            position['qty'] = new_qty
            
        elif side == 'sell':
            self.store.balance[self.name] += (cost - fee)
            position['qty'] -= qty
            # Entry price doesn't change on reduce-only, but resets if flip
            if position['qty'] == 0:
                position['entry_price'] = 0

        # 3. Log Order
        # In a real app, we'd save to DB. For now, just print or store in memory.
        print(f"[Sandbox] {side.upper()} {qty} {symbol} @ {price} (Fee: {fee:.2f})")
        
        # Record trade in store
        trade_record = {
            'timestamp': self.store.current_candle[0] if self.store.current_candle is not None else timestamp,
            'symbol': symbol,
            'side': side,
            'qty': qty,
            'price': price,
            'fee': fee,
            'type': type
        }
        self.store.trades.append(trade_record)
        
        return order_id

    def market_order(self, symbol, qty, side):
        # In backtest, we need the current price. 
        # The store should hold the current price of the simulation.
        price = self.store.price
        return self.process_order(symbol, qty, price, side, 'MARKET')
