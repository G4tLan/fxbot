from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Exchange(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def fetch_ohlcv(self, symbol: str, timeframe: str, start_ts: int, end_ts: int = None) -> List[Dict[str, Any]]:
        """
        Fetch OHLCV data.
        """
        pass

    def get_current_price(self, symbol: str) -> float:
        pass

    def market_order(self, symbol: str, qty: float, side: str):
        pass

    def limit_order(self, symbol: str, qty: float, price: float, side: str):
        pass
