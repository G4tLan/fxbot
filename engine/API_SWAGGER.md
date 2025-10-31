# FXBot Engine API Documentation

This document describes the REST API endpoints provided by the FXBot Engine Flask server. All endpoints return JSON responses.

---

## Base URL

```
http://localhost:5000/
```

---

## Endpoints


### 1. Get Available Filters

**GET** `/filters`

**Example Request:**
```
GET http://localhost:5000/filters
```

**Example Response:**
```json
[
  {
    "ticker": "EURUSD=X",
    "intervals": [
      {
        "interval": "5m",
        "runs": [
          { "run_name": "run-1", "dates": ["2025-10-27"] }
        ]
      }
    ]
  }
]
```

---


### 2. Get Candles Data

**GET** `/candles`

**Query Parameters:**
- `ticker` (required)
- `interval` (required)
- `run_name` (required)

**Example Request:**
```
GET http://localhost:5000/candles?ticker=EURUSD=X&interval=5m&run_name=run-1
```

**Example Response:**
```json
[
  {
    "datetime": "2025-10-27T00:00:00+00:00",
    "High": 1.163602590560913,
    "Low": 1.1634671688079834,
    "Close": 1.1634671688079834,
    "Open": 1.1634671688079834,
    "Volume": 0.0
  },
  {
    "datetime": "2025-10-27T00:05:00+00:00",
    "High": 1.1633317470550537,
    "Low": 1.1633317470550537,
    "Close": 1.1633317470550537,
    "Open": 1.1633317470550537,
    "Volume": 0.0
  }
]
```

---


### 3. Get Equity Data

**GET** `/equity`

**Query Parameters:**
- `ticker` (required)
- `interval` (required)
- `run_name` (required)

**Example Request:**
```
GET http://localhost:5000/equity?ticker=EURUSD=X&interval=5m&run_name=run-1
```

**Example Response:**
```json
[
  {
    "datetime": "2025-10-27T00:00:00+00:00",
    "equity": 10000.0,
    "current_balance": 10000.0,
    "unrealised_pnl": 0.0,
    "max_equity_so_far": 10000.0,
    "min_equity_so_far": 10000.0
  },
  {
    "datetime": "2025-10-27T00:05:00+00:00",
    "equity": 10000.0,
    "current_balance": 10000.0,
    "unrealised_pnl": 0.0,
    "max_equity_so_far": 10000.0,
    "min_equity_so_far": 10000.0
  }
]
```

---


### 4. Get Trades Data

**GET** `/trades`

**Query Parameters:**
- `ticker` (required)
- `interval` (required)
- `run_name` (required)

**Example Request:**
```
GET http://localhost:5000/trades?ticker=EURUSD=X&interval=5m&run_name=run-1
```

**Example Response:**
```json
{
  "options": {
    "start_date": "2025-10-27",
    "end_date": "2025-10-27",
    "interval": "5m",
    "ticker": "EURUSD=X",
    "save_location_base": "test_results",
    "ema_short": 8,
    "ema_long": 34,
    "window": 20,
    "threshold_bb": 0.7,
    "threshold_adx": 20,
    "tolerance": 0.4,
    "loops": 3,
    "results_file_dir": "test_results/EURUSD=X/5m/run-1"
  },
  "active_trades": [
    {
      "entry_id": "f5f5185f-e843-4ca8-966f-21602a778980",
      "ticker": "EURUSD=X"
      // ...
    }
  ]
}
```

---


### 5. Get Daily Payloads

**GET** `/payloads`

**Query Parameters:**
- `ticker` (required)
- `interval` (required)
- `run_name` (required)
- `date` (required, format: YYYY-MM-DD)

**Example Request:**
```
GET http://localhost:5000/payloads?ticker=EURUSD=X&interval=5m&run_name=run-1&date=2025-10-27
```

**Example Response:**
```json
{
  "options": {
    "start_date": "2025-10-27",
    "end_date": "2025-10-27",
    "interval": "5m",
    "ticker": "EURUSD=X",
    "save_location_base": "test_results",
    "ema_short": 8,
    "ema_long": 34,
    "window": 20,
    "threshold_bb": 0.7,
    "threshold_adx": 20,
    "tolerance": 0.4,
    "loops": 3,
    "results_file_dir": "test_results/EURUSD=X/5m/run-1"
  },
  "payloads": [
    {
      "payload": {
        "strategy_type": "consolidation_breakout"
        // ...
      }
    }
  ]
}
```

---


### 6. Get Indicators

**GET** `/indicators`

**Query Parameters:**
- `ticker` (required)
- `interval` (required)
- `run_name` (required)
- `key` (optional, case-insensitive)

**Example Request (all indicators):**
```
GET http://localhost:5000/indicators?ticker=EURUSD=X&interval=5m&run_name=run-1
```

**Example Response (all indicators):**
```json
{
    "SMA": [
        {
            "datetime": "2025-10-27T00:00:00+00:00",
            "value": 1.1634671688079834
        },
        {
            "datetime": "2025-10-27T00:05:00+00:00",
            "value": 1.1633994579315186
        }
    ]
    // ...
}
```

**Example Request (single indicator):**
```
GET http://localhost:5000/indicators?ticker=EURUSD=X&interval=5m&run_name=run-1&key=sma
```

**Example Response (single indicator):**
```json
{
    "SMA": [
        {
            "datetime": "2025-10-27T00:00:00+00:00",
            "value": 1.1634671688079834
        },
        {
            "datetime": "2025-10-27T00:05:00+00:00",
            "value": 1.1633994579315186
        }
    ]
}
```

---

## Error Responses
- All endpoints return a JSON error message and appropriate HTTP status code if required parameters are missing or data is not found.

---

## Notes
- All endpoints use HTTP GET.
- All responses are in JSON format.
- For production, set `debug=False` in the Flask app.
