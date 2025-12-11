import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.main import app

class TestPhase5(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "online", "message": "FXBot Engine is running"})

    @patch('engine.controllers.import_controller.run_import')
    def test_import_endpoint(self, mock_run_import):
        # Test triggering import
        payload = {
            "exchange": "Binance",
            "symbol": "BTC-USDT",
            "start_date": "2023-01-01"
        }
        response = self.client.post("/api/v1/import", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'queued')
        
        # Note: Background tasks are not executed immediately by TestClient unless configured,
        # but the endpoint logic is tested.

    @patch('engine.controllers.backtest_controller.run_backtest')
    def test_backtest_endpoint(self, mock_run_backtest):
        # Mock return value
        mock_run_backtest.return_value = {
            "initial_balance": 10000,
            "final_balance": 10500,
            "pnl_percent": 5.0,
            "trades": []
        }

        payload = {
            "exchange": "Sandbox",
            "symbol": "BTC-USDT",
            "timeframe": "1h",
            "start_date": "2023-01-01",
            "end_date": "2023-01-05",
            "strategy_name": "SimpleStrategy"
        }
        
        response = self.client.post("/api/v1/backtest", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results']['pnl_percent'], 5.0)
        
        mock_run_backtest.assert_called_once()

if __name__ == '__main__':
    unittest.main()
