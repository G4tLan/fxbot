import sys
import os

# Add the parent directory to sys.path so we can import 'engine'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.config import db
from engine.models import (
    Candle, ClosedTrade, Order, Trade, Log, Option, ExchangeApiKeys,
    Ticker, Orderbook, DailyBalance, MonteCarloSession, OptimizationSession, NotificationApiKeys,
    User, Task
)

def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([
        Candle, ClosedTrade, Order, Trade, Log, Option, ExchangeApiKeys,
        Ticker, Orderbook, DailyBalance, MonteCarloSession, OptimizationSession, NotificationApiKeys,
        User, Task
    ])
    if not db.is_closed():
        db.close()
    print("Database initialized.")

if __name__ == "__main__":
    init_db()
