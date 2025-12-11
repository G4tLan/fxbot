from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Exchange(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def fetch_ohlcv(self, symbol: str, timeframe: str, start_ts: int, end_ts: int = None) -> List[Dict[str, Any]]:
        """
        Fetch OHLCV data.
        
        :param symbol: The trading symbol (e.g., 'BTC-USDT')
        :param timeframe: The timeframe (e.g., '1m', '1h', '1d')
        :param start_ts: Start timestamp in milliseconds
        :param end_ts: End timestamp in milliseconds (optional)
        :return: List of dictionaries with keys: timestamp, open, high, low, close, volume
        """
        pass
