import requests
import time
from typing import List, Dict, Any
from engine.exchanges.exchange import Exchange

class Binance(Exchange):
    def __init__(self):
        super().__init__('Binance')
        self.base_url = "https://api.binance.com"

    def fetch_ohlcv(self, symbol: str, timeframe: str, start_ts: int, end_ts: int = None) -> List[Dict[str, Any]]:
        # Convert symbol format if necessary (e.g., BTC-USDT -> BTCUSDT)
        symbol_clean = symbol.replace('-', '').replace('/', '')
        
        limit = 1000
        candles = []
        current_start = start_ts

        while True:
            params = {
                'symbol': symbol_clean,
                'interval': timeframe,
                'startTime': current_start,
                'limit': limit
            }
            if end_ts:
                params['endTime'] = end_ts

            try:
                response = requests.get(f"{self.base_url}/api/v3/klines", params=params)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                print(f"Error fetching data from Binance: {e}")
                break

            if not data:
                break

            for row in data:
                # Binance format: [timestamp, open, high, low, close, volume, close_time, ...]
                candle = {
                    'timestamp': int(row[0]),
                    'open': float(row[1]),
                    'high': float(row[2]),
                    'low': float(row[3]),
                    'close': float(row[4]),
                    'volume': float(row[5])
                }
                candles.append(candle)

            # Check if we fetched fewer than limit, meaning we reached the end
            if len(data) < limit:
                break
            
            # Update start time for next batch (last candle timestamp + 1ms)
            last_ts = int(data[-1][0])
            current_start = last_ts + 1
            
            # Safety break if we passed end_ts
            if end_ts and current_start > end_ts:
                break
                
            # Respect rate limits
            time.sleep(0.1)

        return candles
