from engine.store import store
import numpy as np

class Position:
    def __init__(self, qty=0, entry_price=0, current_price=0):
        self.qty = qty
        self.entry_price = entry_price
        self.current_price = current_price
    
    @property
    def pnl(self):
        if self.qty == 0: return 0
        if self.qty > 0:
            return (self.current_price - self.entry_price) * self.qty
        else:
            return (self.entry_price - self.current_price) * abs(self.qty)
    
    @property
    def value(self):
        return abs(self.qty) * self.current_price

class Strategy:
    def __init__(self, symbol, exchange, timeframe):
        self.symbol = symbol
        self.exchange = exchange
        self.timeframe = timeframe
        self._candles = np.array([])
        
        # Order intents
        self._buy = []
        self._sell = []
        self._stop_loss = []
        self._take_profit = []

    @property
    def candles(self):
        return self._candles
        
    @candles.setter
    def candles(self, value):
        self._candles = value

    @property
    def price(self):
        if len(self._candles) > 0:
            return self._candles[-1][4]
        return 0

    @property
    def time(self):
        if len(self._candles) > 0:
            return self._candles[-1][0]
        return 0

    @property
    def balance(self):
        # Returns the available balance for the exchange
        return store.balance.get(self.exchange, 0)

    @property
    def position(self):
        # Get position from store
        # Key format: "Exchange-Symbol"
        key = f"{self.exchange}-{self.symbol}"
        pos_data = store.positions.get(key, {'qty': 0, 'entry_price': 0})
        return Position(pos_data['qty'], pos_data['entry_price'], self.price)
    
    @property
    def portfolio_value(self):
        return self.balance + self.position.pnl # Simplified

    # --- Order Management Properties ---
    
    @property
    def buy(self): return self._buy
    @buy.setter
    def buy(self, value):
        if isinstance(value, tuple): self._buy = [value]
        elif isinstance(value, list): self._buy = value
        
    @property
    def sell(self): return self._sell
    @sell.setter
    def sell(self, value):
        if isinstance(value, tuple): self._sell = [value]
        elif isinstance(value, list): self._sell = value

    @property
    def stop_loss(self): return self._stop_loss
    @stop_loss.setter
    def stop_loss(self, value):
        if isinstance(value, tuple): self._stop_loss = [value]
        elif isinstance(value, list): self._stop_loss = value

    @property
    def take_profit(self): return self._take_profit
    @take_profit.setter
    def take_profit(self, value):
        if isinstance(value, tuple): self._take_profit = [value]
        elif isinstance(value, list): self._take_profit = value

    # --- Lifecycle Methods ---

    def setUp(self):
        """Called before the strategy starts."""
        pass

    def terminate(self):
        """Called after the strategy ends."""
        pass

    def update_position(self):
        """Called on every candle if there is an open position."""
        pass

    def should_long(self) -> bool:
        """Return True to signal a Long entry."""
        return False

    def should_short(self) -> bool:
        """Return True to signal a Short entry."""
        return False

    def should_cancel(self) -> bool:
        """Return True to cancel pending entry orders."""
        return False
    
    def go_long(self):
        """Define entry order, stop-loss, and take-profit for Long."""
        pass

    def go_short(self):
        """Define entry order, stop-loss, and take-profit for Short."""
        pass
