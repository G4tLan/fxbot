import numpy as np
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.strategies.Strategy import Strategy
import engine.indicators as ta
from engine.services.cache import cached

# Mock Store
from engine.store import store
store.balance = {'Binance': 10000}
store.positions = {'Binance-BTC-USDT': {'qty': 1, 'entry_price': 50000}}

class MyStrategy(Strategy):
    def setUp(self):
        print("Setting up strategy...")

    @property
    @cached
    def rsi(self):
        return ta.rsi(self.candles, period=14)

    def should_long(self):
        # Check if RSI < 30
        if len(self.rsi) > 0 and self.rsi[-1] < 30:
            return True
        return False

    def go_long(self):
        qty = 1
        price = self.price
        self.buy = (qty, price)
        print(f"Going Long at {price}")

def run_test():
    # Create dummy candles (100 candles)
    # timestamp, open, high, low, close, volume
    candles = np.zeros((100, 6))
    # Make price go down to trigger RSI < 30
    for i in range(100):
        price = 100 - i * 0.5
        candles[i] = [i, price, price+1, price-1, price, 100]

    strategy = MyStrategy("BTC-USDT", "Binance", "1h")
    strategy.setUp()
    
    # Simulate loop
    for i in range(20, 100):
        # Slice candles up to current point
        strategy.candles = candles[:i+1]
        
        # print(f"Time: {strategy.time}, Price: {strategy.price}, RSI: {strategy.rsi[-1]:.2f}")
        
        if strategy.should_long():
            print(f"Time: {strategy.time}, Price: {strategy.price}, RSI: {strategy.rsi[-1]:.2f}")
            strategy.go_long()
            print("Signal detected!")
            break

if __name__ == "__main__":
    run_test()
