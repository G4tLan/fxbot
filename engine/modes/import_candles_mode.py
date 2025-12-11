import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.exchanges.binance import Binance
from engine.exchanges.yahoo import Yahoo
from engine.models.core import Candle
from engine.config import db
import time

def run_import(exchange_name: str, symbol: str, start_date: str, timeframe: str = '1h'):
    """
    Import candles from an exchange.
    
    :param exchange_name: Name of the exchange (e.g., 'Binance')
    :param symbol: Symbol to fetch (e.g., 'BTC-USDT')
    :param start_date: Start date in 'YYYY-MM-DD' format
    :param timeframe: Timeframe to fetch (e.g., '1m', '1h', '1d')
    """
    print(f"Starting import for {symbol} from {exchange_name} since {start_date} ({timeframe})...")
    
    # 1. Resolve Driver
    if exchange_name.lower() == 'binance':
        driver = Binance()
    elif exchange_name.lower() == 'yahoo':
        driver = Yahoo()
    else:
        raise ValueError(f"Exchange {exchange_name} not supported.")

    # 2. Parse Date to Timestamp
    try:
        start_ts = int(time.mktime(time.strptime(start_date, "%Y-%m-%d"))) * 1000
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    # 3. Fetch Data
    candles_data = driver.fetch_ohlcv(symbol, timeframe, start_ts)
    
    print(f"Fetched {len(candles_data)} candles.")

    # 4. Store in DB
    if not candles_data:
        print("No data found.")
        return

    print("Saving to database...")
    
    # Bulk insert is faster
    # We need to map the dict to the model fields
    batch_size = 500
    total = len(candles_data)
    
    with db.atomic():
        for i in range(0, total, batch_size):
            batch = candles_data[i:i+batch_size]
            data_to_insert = []
            for c in batch:
                data_to_insert.append({
                    'timestamp': c['timestamp'],
                    'open': c['open'],
                    'high': c['high'],
                    'low': c['low'],
                    'close': c['close'],
                    'volume': c['volume'],
                    'exchange': exchange_name,
                    'symbol': symbol
                })
            
            # Upsert (replace if exists)
            Candle.insert_many(data_to_insert).on_conflict_replace().execute()
            print(f"Saved {min(i+batch_size, total)}/{total}")

    print("Import complete.")

if __name__ == "__main__":
    # Example usage
    run_import('Binance', 'BTC-USDT', '2023-01-01')
