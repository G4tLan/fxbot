from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
from engine.models.core import Order

class Exchange(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def fetch_ohlcv(self, symbol: str, timeframe: str, start_ts: int, end_ts: int = None) -> List[Dict[str, Any]]:
        """
        Fetch OHLCV data.
        """
        pass

    @abstractmethod
    def market_order(self, symbol: str, qty: float, current_price: float, side: str, reduce_only: bool) -> Order:
        pass

    @abstractmethod
    def limit_order(self, symbol: str, qty: float, price: float, side: str, reduce_only: bool) -> Order:
        pass

    @abstractmethod
    def stop_order(self, symbol: str, qty: float, price: float, side: str, reduce_only: bool) -> Order:
        pass

    @abstractmethod
    def cancel_all_orders(self, symbol: str) -> None:
        pass

    @abstractmethod
    def cancel_order(self, symbol: str, order_id: str) -> None:
        pass

    @abstractmethod
    def _fetch_precisions(self) -> None:
        pass
