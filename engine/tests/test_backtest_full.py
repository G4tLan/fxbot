import unittest
import time
import json
import uuid
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from engine.main import app
from engine.models.core import User, BacktestSession, Log
from engine.init_db import init_db
from engine.schemas import BacktestResult, TradeResult, ClosedTradeResult

class TestBacktestFull(unittest.TestCase):
    def setUp(self):
        init_db()
        self.client = TestClient(app)
        self.username = f"user_{int(time.time())}_{uuid.uuid4().hex[:6]}"
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

    @patch("engine.controllers.backtest_controller.run_backtest")
    def test_backtest_success_flow(self, mock_run_backtest):
        """
        Test the complete flow of a successful backtest:
        Trigger -> Background Execution -> Session Update -> Result Retrieval
        """
        # Mock return value
        mock_result = BacktestResult(
            initial_balance=10000.0,
            final_balance=10500.0,
            pnl_percent=5.0,
            trades=[
                TradeResult(timestamp=1000, symbol="BTC-USDT", side="buy", qty=1.0, price=100.0, fee=0.1, type="MARKET"),
                TradeResult(timestamp=2000, symbol="BTC-USDT", side="sell", qty=1.0, price=105.0, fee=0.1, type="MARKET")
            ],
            closed_trades=[
                ClosedTradeResult(entry_price=100.0, exit_price=105.0, qty=1.0, pnl=5.0, opened_at=1000, closed_at=2000, strategy_name="Test", leverage=1, type="long")
            ]
        )
        mock_run_backtest.return_value = mock_result

        # 1. Trigger Backtest
        payload = {
            "exchange": "Binance",
            "symbol": "BTC-USDT",
            "timeframe": "1h",
            "start_date": "2023-01-01",
            "end_date": "2023-01-02",
            "strategy_name": "SimpleStrategy",
            "run_in_background": True
        }
        response = self.client.post("/api/v1/backtest", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "queued")
        task_id = data["task_id"]
        self.assertIsNotNone(task_id)

        # Since TestClient runs background tasks synchronously after the request,
        # the session should already be 'completed' in the DB by now.
        
        # 2. Verify Session Status in DB
        session = BacktestSession.get(BacktestSession.id == task_id)
        self.assertEqual(session.status, "completed")
        self.assertIsNotNone(session.metrics)
        metrics = json.loads(session.metrics)
        self.assertEqual(metrics["final_balance"], 10500.0)
        
        # 3. Verify Trades and Closed Trades
        trades = json.loads(session.trades)
        self.assertEqual(len(trades), 2)
        closed_trades = json.loads(session.closed_trades)
        self.assertEqual(len(closed_trades), 1)
        self.assertEqual(closed_trades[0]["pnl"], 5.0)

        # 4. Retrieve via API
        response = self.client.get(f"/api/v1/sessions/{task_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "completed")
        self.assertEqual(len(data["trades"]), 2)
        self.assertEqual(len(data["closed_trades"]), 1)

    @patch("engine.controllers.backtest_controller.run_backtest")
    def test_backtest_failure_flow(self, mock_run_backtest):
        """
        Test the flow when backtest raises an exception.
        """
        mock_run_backtest.side_effect = ValueError("Not enough data")

        payload = {
            "exchange": "Binance",
            "symbol": "BTC-USDT",
            "timeframe": "1h",
            "start_date": "2023-01-01",
            "end_date": "2023-01-02",
            "strategy_name": "SimpleStrategy",
            "run_in_background": True
        }
        response = self.client.post("/api/v1/backtest", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        task_id = response.json()["task_id"]

        # Verify Session Status is 'failed'
        session = BacktestSession.get(BacktestSession.id == task_id)
        self.assertEqual(session.status, "failed")
        self.assertIn("Not enough data", session.exception)

    def test_session_management(self):
        """
        Test listing, deleting, and updating sessions.
        """
        # Create dummy sessions
        ids = []
        for i in range(3):
            sid = str(uuid.uuid4())
            ids.append(sid)
            BacktestSession.create(
                id=sid,
                status="completed",
                created_at=int(time.time() * 1000) + i, # different times
                updated_at=int(time.time() * 1000) + i
            )

        # 1. List Sessions
        response = self.client.post("/api/v1/sessions", json={"page": 1, "limit": 10}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(data["count"], 3)
        # Check sorting (descending updated_at)
        # The last created one (highest timestamp) should be first
        self.assertEqual(data["sessions"][0]["id"], ids[2])

        # 2. Update Notes
        target_id = ids[0]
        notes_payload = {
            "title": "My Best Run",
            "description": "Testing moving average"
        }
        response = self.client.post(f"/api/v1/sessions/{target_id}/notes", json=notes_payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        session = BacktestSession.get(BacktestSession.id == target_id)
        self.assertEqual(session.title, "My Best Run")

        # 3. Update State
        state_payload = {
            "id": target_id,
            "state": {"step": 5, "vars": {"a": 1}}
        }
        response = self.client.post("/api/v1/update-state", json=state_payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        session = BacktestSession.get(BacktestSession.id == target_id)
        self.assertEqual(json.loads(session.state)["step"], 5)

        # 4. Delete Session
        response = self.client.delete(f"/api/v1/sessions/{target_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        with self.assertRaises(BacktestSession.DoesNotExist):
            BacktestSession.get(BacktestSession.id == target_id)

    def test_cancel_backtest(self):
        """
        Test cancelling a backtest.
        """
        sid = str(uuid.uuid4())
        BacktestSession.create(
            id=sid,
            status="processing",
            created_at=int(time.time() * 1000),
            updated_at=int(time.time() * 1000)
        )

        response = self.client.post("/api/v1/cancel", json={"id": sid}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        session = BacktestSession.get(BacktestSession.id == sid)
        self.assertEqual(session.status, "cancelled")

    def test_purge_sessions(self):
        """
        Test purging old sessions.
        """
        # Create old session (10 days ago)
        old_id = str(uuid.uuid4())
        BacktestSession.create(
            id=old_id,
            status="completed",
            created_at=int(time.time() * 1000) - (10 * 86400 * 1000) - 1000, # 10 days + 1 sec ago
            updated_at=int(time.time() * 1000)
        )
        
        # Create new session (1 day ago)
        new_id = str(uuid.uuid4())
        BacktestSession.create(
            id=new_id,
            status="completed",
            created_at=int(time.time() * 1000) - (1 * 86400 * 1000),
            updated_at=int(time.time() * 1000)
        )

        # Purge older than 5 days
        response = self.client.post("/api/v1/purge-sessions", json={"days_old": 5}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(data["deleted_count"], 1)

        # Verify old is gone, new remains
        with self.assertRaises(BacktestSession.DoesNotExist):
            BacktestSession.get(BacktestSession.id == old_id)
            
        self.assertTrue(BacktestSession.select().where(BacktestSession.id == new_id).exists())

    def test_misc_endpoints(self):
        """
        Test strategies, chart-data, and logs endpoints.
        """
        # 1. Strategies
        response = self.client.get("/api/v1/strategies", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("SimpleStrategy", response.json()["strategies"])

        # 2. Chart Data
        sid = str(uuid.uuid4())
        chart_data = {"candles": [[1000, 10, 20, 5, 15, 100]]}
        BacktestSession.create(
            id=sid,
            status="completed",
            chart_data=json.dumps(chart_data),
            created_at=int(time.time() * 1000),
            updated_at=int(time.time() * 1000)
        )
        
        response = self.client.get(f"/api/v1/sessions/{sid}/chart-data", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["chart_data"], chart_data)

        # 3. Logs (File based)
        # We need to mock os.path.exists and open, or just create a dummy file
        import os
        log_dir = "storage/logs/backtest-mode"
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f"{sid}.txt")
        with open(log_path, "w") as f:
            f.write("Test Log Content")
            
        response = self.client.get(f"/api/v1/sessions/{sid}/logs", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "Test Log Content")
        
        # Cleanup
        if os.path.exists(log_path):
            os.remove(log_path)

if __name__ == "__main__":
    unittest.main()
