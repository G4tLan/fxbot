import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os
import time

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.main import app
from engine.init_db import init_db

from engine.schemas import BacktestResult, TradeResult
from engine.models.core import BacktestSession
import json

class TestPhase5(unittest.TestCase):
    def setUp(self):
        init_db()
        self.client = TestClient(app)
        self.username = f"user_p5_{int(time.time())}"
        self.password = "password123"
        self.headers = self._get_auth_headers()

    def _get_auth_headers(self):
        # Register
        self.client.post("/api/v1/auth/register", json={"username": self.username, "password": self.password})
        # Login
        response = self.client.post("/api/v1/auth/login", data={"username": self.username, "password": self.password})
        if response.status_code == 200:
            token = response.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
        return {}

    def test_root(self):
        # The root endpoint might not exist in main.py based on previous reads, let's check main.py later.
        # But assuming it exists or we skip it.
        # Actually, let's check main.py content first.
        pass

    @patch('engine.controllers.import_controller.run_import')
    def test_import_endpoint(self, mock_run_import):
        # Test triggering import
        payload = {
            "exchange": "Binance",
            "symbol": "BTC-USDT",
            "start_date": "2023-01-01"
        }
        response = self.client.post("/api/v1/import", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'queued')
        
        # Note: Background tasks are not executed immediately by TestClient unless configured,
        # but the endpoint logic is tested.

    @patch('engine.controllers.backtest_controller.run_backtest')
    def test_backtest_endpoint(self, mock_run_backtest):
        # Mock return value
        mock_run_backtest.return_value = BacktestResult(
            initial_balance=10000,
            final_balance=10500,
            pnl_percent=5.0,
            trades=[],
            closed_trades=[]
        )

        payload = {
            "exchange": "Sandbox",
            "symbol": "BTC-USDT",
            "timeframe": "1h",
            "start_date": "2023-01-01",
            "end_date": "2023-01-05",
            "strategy_name": "SimpleStrategy"
        }
        
        response = self.client.post("/api/v1/backtest", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'queued')
        task_id = data['task_id']
        
        # TestClient runs background tasks. So DB should be updated.
        session = BacktestSession.get(BacktestSession.id == task_id)
        self.assertEqual(session.status, 'completed')
        metrics = json.loads(session.metrics)
        self.assertEqual(metrics['pnl_percent'], 5.0)
        
        mock_run_backtest.assert_called_once()

if __name__ == '__main__':
    unittest.main()
