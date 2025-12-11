import unittest
import time
from fastapi.testclient import TestClient
from engine.main import app
from engine.init_db import init_db

class TestPhase6(unittest.TestCase):
    def setUp(self):
        init_db()
        self.client = TestClient(app)
        self.username = f"user_p6_{int(time.time())}"
        self.password = "password123"
        self.headers = self._get_auth_headers()
        self.token = self.headers.get("Authorization", "").replace("Bearer ", "")

    def _get_auth_headers(self):
        # Register
        self.client.post("/api/v1/auth/register", json={"username": self.username, "password": self.password})
        # Login
        response = self.client.post("/api/v1/auth/login", data={"username": self.username, "password": self.password})
        if response.status_code == 200:
            token = response.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
        return {}

    def test_lsp_config(self):
        response = self.client.get("/api/v1/lsp-config", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("ws_port", data)
        self.assertIn("ws_path", data)
        self.assertTrue(data["enabled"])

    def test_config_get(self):
        response = self.client.post("/api/v1/config/get", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("app", data)
        self.assertIn("database", data)

    def test_config_update(self):
        # Initial check
        response = self.client.post("/api/v1/config/get", headers=self.headers)
        initial_debug = response.json()["app"]["debug"]

        # Update
        new_debug = not initial_debug
        response = self.client.post("/api/v1/config/update", json={"updates": {"app": {"debug": new_debug}}}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        response = self.client.post("/api/v1/config/get", headers=self.headers)
        self.assertEqual(response.json()["app"]["debug"], new_debug)

    def test_websocket(self):
        with self.client.websocket_connect(f"/ws?token={self.token}") as websocket:
            websocket.send_text("Hello WebSocket")
            data = websocket.receive_text()
            self.assertEqual(data, "Message text was: Hello WebSocket")

if __name__ == '__main__':
    unittest.main()
