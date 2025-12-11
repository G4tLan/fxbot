import unittest
from fastapi.testclient import TestClient
from engine.main import app

class TestPhase6(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_lsp_config(self):
        response = self.client.get("/api/v1/lsp-config")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("ws_port", data)
        self.assertIn("ws_path", data)
        self.assertTrue(data["enabled"])

    def test_config_get(self):
        response = self.client.post("/api/v1/config/get")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("app", data)
        self.assertIn("database", data)

    def test_config_update(self):
        # Initial check
        response = self.client.post("/api/v1/config/get")
        initial_debug = response.json()["app"]["debug"]

        # Update
        new_debug = not initial_debug
        response = self.client.post("/api/v1/config/update", json={"updates": {"app": {"debug": new_debug}}})
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        response = self.client.post("/api/v1/config/get")
        self.assertEqual(response.json()["app"]["debug"], new_debug)

    def test_websocket(self):
        with self.client.websocket_connect("/ws") as websocket:
            websocket.send_text("Hello WebSocket")
            data = websocket.receive_text()
            self.assertEqual(data, "Message text was: Hello WebSocket")

if __name__ == '__main__':
    unittest.main()
