import unittest
from fastapi.testclient import TestClient
from engine.main import app
from engine.models.core import User
from engine.init_db import init_db

class TestSecuredEndpoints(unittest.TestCase):
    def setUp(self):
        init_db()
        self.client = TestClient(app)
        
        # Create a user and get token
        self.username = "secureuser"
        self.password = "securepass"
        self.client.post("/api/v1/auth/register", json={"username": self.username, "password": self.password})
        response = self.client.post("/api/v1/auth/login", data={"username": self.username, "password": self.password})
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_unauthorized_access(self):
        # Try accessing endpoints without token
        endpoints = [
            ("POST", "/api/v1/import", {"exchange": "Binance", "symbol": "BTC-USDT", "start_date": "2023-01-01"}),
            ("POST", "/api/v1/backtest", {"exchange": "Binance", "symbol": "BTC-USDT", "timeframe": "1h", "start_date": "2023-01-01", "end_date": "2023-01-02", "strategy_name": "SimpleStrategy"}),
            ("POST", "/api/v1/config/get", {}),
            ("GET", "/api/v1/exchange/api-keys", None),
            ("GET", "/api/v1/lsp-config", None)
        ]
        
        for method, url, json_data in endpoints:
            if method == "POST":
                response = self.client.post(url, json=json_data)
            else:
                response = self.client.get(url)
            self.assertEqual(response.status_code, 401, f"Endpoint {url} should be unauthorized")

    def test_authorized_access(self):
        # Try accessing endpoints with token
        
        # Config Get
        response = self.client.post("/api/v1/config/get", json={}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        # LSP Config
        response = self.client.get("/api/v1/lsp-config", headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_websocket_auth(self):
        # Without token
        with self.assertRaises(Exception): # WebSocketDisconnect or similar
             with self.client.websocket_connect("/ws") as websocket:
                pass
        
        # With token
        with self.client.websocket_connect(f"/ws?token={self.token}") as websocket:
            websocket.send_text("Hello")
            data = websocket.receive_text()
            self.assertIn("Hello", data)

if __name__ == '__main__':
    unittest.main()
