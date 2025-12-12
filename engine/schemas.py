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

class BacktestResult(BaseModel):
    initial_balance: float
    final_balance: float
    pnl_percent: float
    trades: List[TradeResult]
