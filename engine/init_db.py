import sys
import os

# Add the parent directory to sys.path so we can import 'engine'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.config import db
from engine.models import (
    Candle, ClosedTrade, Order, Trade, BacktestSession, Log, Option, ExchangeApiKeys,
    Ticker, Orderbook, DailyBalance, MonteCarloSession, OptimizationSession, NotificationApiKeys
)

def init_db():
    db.connect()
    db.create_tables([
        Candle, ClosedTrade, Order, Trade, BacktestSession, Log, Option, ExchangeApiKeys,
        Ticker, Orderbook, DailyBalance, MonteCarloSession, OptimizationSession, NotificationApiKeys
    ])
    print("Database initialized.")

if __name__ == "__main__":
    init_db()
