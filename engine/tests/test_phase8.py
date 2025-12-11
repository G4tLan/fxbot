import unittest
import time
import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from engine.main import app
from engine.models.core import Task, User
from engine.init_db import init_db

class TestPhase8(unittest.TestCase):
    def setUp(self):
        init_db()
        self.client = TestClient(app)
        self.username = f"user_{int(time.time())}"
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

    @patch("engine.controllers.import_controller.run_import")
    def test_import_task_flow(self, mock_run_import):
        # 1. Trigger Import
        payload = {
            "exchange": "Binance",
            "symbol": "BTC-USDT",
            "start_date": "2023-01-01"
        }
        response = self.client.post("/api/v1/import", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("task_id", data)
        self.assertEqual(data["status"], "queued")
        task_id = data["task_id"]

        # 2. Check Task Status (Queued/Processing)
        # Since TestClient runs in the same thread/process usually, background tasks might run after the response
        # But with TestClient, background tasks are executed after the response is returned.
        # So by the time we get here, it might be done if it's fast.
        
        response = self.client.get(f"/api/v1/tasks/{task_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        task_data = response.json()
        self.assertEqual(task_data["id"], task_id)
        self.assertEqual(task_data["type"], "import")
        # It should be completed because mock is instant
        self.assertEqual(task_data["status"], "completed")
        
        mock_run_import.assert_called_once()

    @patch("engine.controllers.backtest_controller.run_backtest")
    def test_backtest_task_flow(self, mock_run_backtest):
        mock_run_backtest.return_value = {"metrics": "good"}
        
        # 1. Trigger Backtest (Background)
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
        self.assertIn("task_id", data)
        task_id = data["task_id"]

        # 2. Check Task Status
        response = self.client.get(f"/api/v1/tasks/{task_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        task_data = response.json()
        self.assertEqual(task_data["status"], "completed")
        # Result is already parsed by the controller if it was a JSON string
        result = task_data["result"]
        self.assertEqual(result["metrics"], "good")

    def test_list_tasks(self):
        # Create a dummy task manually
        task_id = f"manual_task_{int(time.time())}"
        Task.create(
            id=task_id,
            type="test",
            status="queued",
            created_at=int(time.time()),
            updated_at=int(time.time())
        )
        
        response = self.client.get("/api/v1/tasks", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        tasks = response.json()
        self.assertTrue(len(tasks) > 0)
        ids = [t["id"] for t in tasks]
        self.assertIn(task_id, ids)

if __name__ == '__main__':
    unittest.main()
