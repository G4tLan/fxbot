import unittest
import os
import time
from fastapi.testclient import TestClient
from engine.main import app
from engine.models.core import ExchangeApiKeys
from engine.init_db import init_db

class TestPhase7(unittest.TestCase):
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

    def test_auth_flow(self):
        # Use a unique user for this specific test
        username = f"auth_test_{int(time.time())}"
        payload = {"username": username, "password": "password123"}
        
        # 1. Register
        response = self.client.post("/api/v1/auth/register", json=payload)
        self.assertEqual(response.status_code, 200)
        
        # 2. Login
        response = self.client.post("/api/v1/auth/login", data=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        
        # 3. Login Fail
        response = self.client.post("/api/v1/auth/login", data={"username": username, "password": "wrongpassword"})
        self.assertEqual(response.status_code, 401)

    def test_exchange_api_keys_crud(self):
        # 1. Store
        payload = {
            "exchange_name": "Binance",
            "name": "Test Key",
            "api_key": "abc123key",
            "api_secret": "secret456",
            "additional_fields": "{}"
        }
        response = self.client.post("/api/v1/exchange/api-keys/store", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)

        # 2. List
        response = self.client.get("/api/v1/exchange/api-keys", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        keys = response.json()
        self.assertTrue(len(keys) > 0)
        found = False
        key_id = None
        for k in keys:
            if k["api_key"] == "abc123key":
                found = True
                key_id = k["id"]
                self.assertEqual(k["api_secret"], "********") # Check masking
                break
        self.assertTrue(found)

        # 3. Delete
        if key_id:
            response = self.client.post("/api/v1/exchange/api-keys/delete", json={"id": key_id}, headers=self.headers)
            self.assertEqual(response.status_code, 200)
            
            # Verify deletion
            response = self.client.get("/api/v1/exchange/api-keys", headers=self.headers)
            keys = response.json()
            for k in keys:
                self.assertNotEqual(k["id"], key_id)

    def test_supported_symbols(self):
        response = self.client.post("/api/v1/exchange/supported-symbols", json={"exchange_name": "Binance"}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("BTC-USDT", data["symbols"])

if __name__ == '__main__':
    unittest.main()
