import yfinance as yf
from typing import List, Dict, Any
from engine.exchanges.exchange import Exchange
from engine.models.core import Order
import pandas as pd

class Yahoo(Exchange):
    def __init__(self):
        super().__init__('Yahoo')

    def fetch_ohlcv(self, symbol: str, timeframe: str, start_ts: int, end_ts: int = None) -> List[Dict[str, Any]]:
        """
        Fetch OHLCV data from Yahoo Finance.
        
        :param symbol: Ticker symbol (e.g., 'EURUSD=X' for Euro/USD)
        :param timeframe: Timeframe (e.g., '1h', '1d')
        :param start_ts: Start timestamp in milliseconds
        :param end_ts: End timestamp in milliseconds (optional)
        """
        
        # Map timeframe to yfinance interval
        # yfinance supports: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        interval_map = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '1d': '1d',
            '1w': '1wk',
            '1M': '1mo'
        }
        
        interval = interval_map.get(timeframe)
        if not interval:
            raise ValueError(f"Timeframe {timeframe} not supported by Yahoo Finance adapter.")

        # Convert timestamps (ms) to datetime objects or strings
        start_date = pd.to_datetime(start_ts, unit='ms')
        end_date = pd.to_datetime(end_ts, unit='ms') if end_ts else None

        try:
            ticker = yf.Ticker(symbol)
            # fetch data
            df = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if df.empty:
                return []

            candles = []
            for index, row in df.iterrows():
                # Yahoo Finance index is the timestamp
                # Convert to ms
                ts = int(index.timestamp() * 1000)
                
                candle = {
                    'timestamp': ts,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': float(row['Volume'])
                }
                candles.append(candle)
                
            return candles

        except Exception as e:
            print(f"Error fetching data from Yahoo Finance: {e}")
            return []

    def market_order(self, symbol: str, qty: float, current_price: float, side: str, reduce_only: bool) -> Order:
        raise NotImplementedError("Live trading not implemented for Yahoo yet.")

    def limit_order(self, symbol: str, qty: float, price: float, side: str, reduce_only: bool) -> Order:
        raise NotImplementedError("Live trading not implemented for Yahoo yet.")

    def stop_order(self, symbol: str, qty: float, price: float, side: str, reduce_only: bool) -> Order:
        raise NotImplementedError("Live trading not implemented for Yahoo yet.")

    def cancel_all_orders(self, symbol: str) -> None:
        raise NotImplementedError("Live trading not implemented for Yahoo yet.")

    def cancel_order(self, symbol: str, order_id: str) -> None:
        raise NotImplementedError("Live trading not implemented for Yahoo yet.")

    def _fetch_precisions(self) -> None:
        pass
