import unittest
from unittest.mock import MagicMock, patch
import time
from engine.modes.import_candles_mode import run_import

class TestImportTimeframe(unittest.TestCase):
    @patch('engine.modes.import_candles_mode.Binance')
    @patch('engine.modes.import_candles_mode.Candle')
    def test_run_import_passes_timeframe(self, mock_candle_model, mock_binance_class):
        # Setup mock adapter
        mock_adapter = MagicMock()
        mock_adapter.fetch_ohlcv.return_value = []
        mock_binance_class.return_value = mock_adapter

        # Setup mock Candle model
        mock_candle_model.insert_many.return_value.on_conflict_ignore.return_value.execute.return_value = 0

        # Test parameters
        exchange_name = 'binance'
        symbol = 'BTC/USDT'
        start_date = '2023-01-01'
        
        # 1. Test with '1m'
        run_import(exchange_name, symbol, start_date, timeframe='1m')
        
        # Verify fetch_ohlcv was called with timeframe='1m'
        # Note: start_ts calculation depends on timezone, but we can check the other args
        args, kwargs = mock_adapter.fetch_ohlcv.call_args
        self.assertEqual(args[0], symbol)
        self.assertEqual(args[1], '1m')
        # args[2] is start_ts

        # 2. Test with '1h'
        run_import(exchange_name, symbol, start_date, timeframe='1h')
        
        args, kwargs = mock_adapter.fetch_ohlcv.call_args
        self.assertEqual(args[0], symbol)
        self.assertEqual(args[1], '1h')

if __name__ == '__main__':
    unittest.main()
