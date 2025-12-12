from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class TradeResult(BaseModel):
    timestamp: int
    symbol: str
    side: str
    qty: float
    price: float
    fee: float
    type: str

class ClosedTradeResult(BaseModel):
    entry_price: float
    exit_price: float
    qty: float
    pnl: float
    opened_at: int
    closed_at: int
    strategy_name: str
    leverage: int
    type: str # long/short

class BacktestResult(BaseModel):
    initial_balance: float
    final_balance: float
    pnl_percent: float
    trades: List[TradeResult]
    closed_trades: List[ClosedTradeResult]
