import unittest
import sys
import os
import numpy as np

# Add parent dir to path
# We need to go up 3 levels: engine/tests/test_phase2.py -> engine/tests -> engine -> fxbot (root)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.strategies.Strategy import Strategy
import engine.indicators as ta
from engine.store import store

class MockStrategy(Strategy):
    def should_long(self):
        # Simple logic: Long if RSI < 30
        rsi = ta.rsi(self.candles, period=14)
        if len(rsi) > 0 and rsi[-1] < 30:
            return True
        return False

    def go_long(self):
        self.buy = (1.0, self.price)

class TestPhase2(unittest.TestCase):
    def setUp(self):
        # Reset store
        store.reset()
        store.balance = {'Binance': 10000}
        
        # Create dummy candles (100 candles)
        # timestamp, open, high, low, close, volume
        self.candles = np.zeros((100, 6))
        # Make price go down to trigger RSI < 30
        for i in range(100):
            price = 100 - i * 0.5
            self.candles[i] = [i, price, price+1, price-1, price, 100]

    def test_strategy_initialization(self):
        strategy = MockStrategy("BTC-USDT", "Binance", "1h")
        self.assertEqual(strategy.symbol, "BTC-USDT")
        self.assertEqual(strategy.balance, 10000)

    def test_indicators(self):
        # Test RSI calculation directly
        rsi = ta.rsi(self.candles, period=14)
        self.assertEqual(len(rsi), 100)
        # RSI should be low because price is dropping
        self.assertTrue(rsi[-1] < 30)

    def test_strategy_logic(self):
        strategy = MockStrategy("BTC-USDT", "Binance", "1h")
        strategy.candles = self.candles
        
        # Check signal
        should_buy = strategy.should_long()
        self.assertTrue(should_buy, "Strategy should signal buy when RSI < 30")
        
        # Execute logic
        if should_buy:
            strategy.go_long()
            
        # Check order intent
        # self.buy is a list of tuples [(qty, price)]
        self.assertEqual(len(strategy.buy), 1)
        self.assertEqual(strategy.buy[0][0], 1.0) # Qty
        self.assertEqual(strategy.buy[0][1], 50.5) # Last price (100 - 99*0.5)

if __name__ == '__main__':
    unittest.main()
