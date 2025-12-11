import unittest
import time
from fastapi.testclient import TestClient
from engine.main import app
from engine.init_db import init_db
from unittest.mock import patch

class TestYahooImport(unittest.TestCase):
    def setUp(self):
        init_db()
        self.client = TestClient(app)
        self.username = f"user_yahoo_{int(time.time())}"
        self.password = "password123"
        self.headers = self._get_auth_headers()

    def _get_auth_headers(self):
        self.client.post("/api/v1/auth/register", json={"username": self.username, "password": self.password})
        response = self.client.post("/api/v1/auth/login", data={"username": self.username, "password": self.password})
        if response.status_code == 200:
            token = response.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
        return {}

    def test_supported_symbols_yahoo(self):
        response = self.client.post("/api/v1/exchange/supported-symbols", json={"exchange_name": "Yahoo"}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("EURUSD=X", data["symbols"])

    @patch('engine.exchanges.yahoo.yf.Ticker')
    def test_yahoo_import_logic(self, mock_ticker):
        # Mock yfinance data
        import pandas as pd
        mock_hist = pd.DataFrame({
            'Open': [1.05, 1.06],
            'High': [1.07, 1.08],
            'Low': [1.04, 1.05],
            'Close': [1.06, 1.07],
            'Volume': [1000, 2000]
        }, index=pd.to_datetime(['2023-01-01 00:00:00', '2023-01-01 01:00:00']))
        
        mock_instance = mock_ticker.return_value
        mock_instance.history.return_value = mock_hist

        from engine.exchanges.yahoo import Yahoo
        driver = Yahoo()
        candles = driver.fetch_ohlcv("EURUSD=X", "1h", 1672531200000) # 2023-01-01
        
        self.assertEqual(len(candles), 2)
        self.assertEqual(candles[0]['open'], 1.05)
        self.assertEqual(candles[0]['timestamp'], 1672531200000)

if __name__ == '__main__':
    unittest.main()
