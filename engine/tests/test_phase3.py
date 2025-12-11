import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.exchanges.binance import Binance

class TestPhase3(unittest.TestCase):
    def setUp(self):
        self.exchange = Binance()

    @patch('engine.exchanges.binance.requests.get')
    def test_fetch_ohlcv(self, mock_get):
        # Mock response data
        # [timestamp, open, high, low, close, volume, ...]
        mock_data = [
            [1600000000000, "100.0", "105.0", "95.0", "102.0", "500.0", 1600000059999],
            [1600000060000, "102.0", "108.0", "101.0", "107.0", "600.0", 1600000119999]
        ]
        
        # Configure the mock to return a response object with .json() method
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Call the method
        candles = self.exchange.fetch_ohlcv('BTC-USDT', '1m', 1600000000000, 1600000120000)

        # Assertions
        self.assertEqual(len(candles), 2)
        self.assertEqual(candles[0]['timestamp'], 1600000000000)
        self.assertEqual(candles[0]['close'], 102.0)
        self.assertEqual(candles[1]['volume'], 600.0)
        
        # Verify requests.get was called with correct params
        mock_get.assert_called()
        args, kwargs = mock_get.call_args
        self.assertIn('params', kwargs)
        self.assertEqual(kwargs['params']['symbol'], 'BTCUSDT')
        self.assertEqual(kwargs['params']['interval'], '1m')

if __name__ == '__main__':
    unittest.main()
