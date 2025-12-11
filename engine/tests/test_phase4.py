import unittest
import sys
import os
import numpy as np
from peewee import SqliteDatabase

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.models.core import Candle
from engine.strategies.Strategy import Strategy
from engine.modes.backtest_mode import run_backtest
from engine.store import store
from engine.config import db

# Use in-memory DB for testing
test_db = SqliteDatabase(':memory:')

class SimpleStrategy(Strategy):
    def should_long(self):
        # Buy on the first available candle after warmup
        # Warmup is 50, so first iteration len is 51
        if len(self.candles) == 51:
            return True
        return False

    def go_long(self):
        self.buy = (1.0, self.price)

class TestPhase4(unittest.TestCase):
    def setUp(self):
        # Bind model to test db
        # Note: In a real scenario, we might need to patch the db proxy in config.py
        # But for now, we'll just use the global db proxy if possible, or re-bind.
        # Since config.py initializes 'db' as a Proxy or Database, we need to be careful.
        # For this test, let's just mock the DB operations or use the actual file if needed,
        # but in-memory is better.
        
        # Re-bind Candle to test_db
        Candle.bind(test_db)
        test_db.connect()
        test_db.create_tables([Candle])
        
        # Insert dummy candles
        # 100 candles
        data = []
        base_ts = 1609459200000 # 2021-01-01
        for i in range(100):
            data.append({
                'timestamp': base_ts + (i * 3600000), # +1 hour
                'open': 100 + i,
                'high': 105 + i,
                'low': 95 + i,
                'close': 100 + i,
                'volume': 1000,
                'exchange': 'Sandbox',
                'symbol': 'BTC-USDT'
            })
        Candle.insert_many(data).execute()

    def tearDown(self):
        test_db.drop_tables([Candle])
        test_db.close()

    def test_backtest_execution(self):
        # Run backtest
        # Dates must cover the generated timestamps
        # 2021-01-01 is start
        
        # We need to patch the time.mktime calls in backtest_mode or pass timestamps directly.
        # The current implementation parses strings.
        
        run_backtest(
            'Sandbox', 
            'BTC-USDT', 
            '1h', 
            '2021-01-01', 
            '2021-01-05', 
            SimpleStrategy
        )
        
        # Check results in Store
        # We expect 1 buy order of 1.0 qty at price ~101 (2nd candle)
        # Initial balance 10000. Cost ~101. Fee ~0.1.
        # Balance should be < 10000
        
        self.assertLess(store.balance['Sandbox'], 10000)
        self.assertEqual(store.positions['Sandbox-BTC-USDT']['qty'], 1.0)

if __name__ == '__main__':
    unittest.main()
