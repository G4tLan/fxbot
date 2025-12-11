import unittest
import sys
import os
from decimal import Decimal
from peewee import SqliteDatabase

# Add parent dir to path to import engine modules
# We need to go up 3 levels: engine/tests/test_phase1.py -> engine/tests -> engine -> fxbot (root)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.models.core import Candle, Order, Trade
from engine.models.base import BaseModel

# Use an in-memory DB for testing
test_db = SqliteDatabase(':memory:')

class TestPhase1(unittest.TestCase):
    def setUp(self):
        # Bind model classes to test db
        test_db.bind([Candle, Order, Trade], bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables([Candle, Order, Trade])

    def tearDown(self):
        test_db.drop_tables([Candle, Order, Trade])
        test_db.close()

    def test_candle_creation(self):
        candle = Candle.create(
            timestamp=1600000000000,
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=500.0,
            exchange='Binance',
            symbol='BTC-USDT'
        )
        
        retrieved = Candle.get(Candle.id == candle.id)
        self.assertEqual(retrieved.symbol, 'BTC-USDT')
        self.assertEqual(retrieved.close, Decimal('102.00000000')) # Decimal precision check

    def test_order_creation(self):
        order = Order.create(
            id='order-123',
            price=50000.0,
            qty=1.5,
            type='LIMIT',
            status='ACTIVE',
            side='buy',
            submitted_at=1600000000000,
            exchange='Binance',
            symbol='BTC-USDT'
        )
        
        retrieved = Order.get(Order.id == 'order-123')
        self.assertEqual(retrieved.status, 'ACTIVE')
        self.assertEqual(retrieved.qty, Decimal('1.50000000'))

if __name__ == '__main__':
    unittest.main()
