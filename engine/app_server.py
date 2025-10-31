import os
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

# --- Configuration ---
RESULTS_BASE_DIR = os.path.join(os.path.dirname(__file__), 'test_results')

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app) # This will enable CORS for all routes and origins

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper for JSON Serialization of datetime objects ---
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

# --- Helper to load JSON files ---
def _load_json_file(filepath):
    """Loads a JSON file and returns its content."""
    if not os.path.exists(filepath):
        logging.warning(f"File not found: {filepath}")
        return None
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {filepath}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error reading file {filepath}: {e}")
        return None

# --- Endpoint: Get all available filters ---
@app.route('/filters', methods=['GET'])
def get_filters():
    """
    Returns a JSON structure detailing all available backtest results,
    including tickers, intervals, backtest start dates, run names, and daily payload dates.
    """
    filters = []
    if not os.path.exists(RESULTS_BASE_DIR):
        return jsonify({"error": "Results directory not found."}), 404

    for ticker_dir in os.listdir(RESULTS_BASE_DIR):
        ticker_path = os.path.join(RESULTS_BASE_DIR, ticker_dir)
        if not os.path.isdir(ticker_path):
            continue

        ticker_data = {"ticker": ticker_dir, "intervals": []}
        for interval_dir in os.listdir(ticker_path):
            interval_path = os.path.join(ticker_path, interval_dir)
            if not os.path.isdir(interval_path): continue

            interval_data = {"interval": interval_dir, "runs": []}
            for run_dir in os.listdir(interval_path):
                run_path = os.path.join(interval_path, run_dir)
                if not os.path.isdir(run_path) or not run_dir.startswith('run-'): continue

                run_data = {"run_name": run_dir, "dates": []}
                
                # Attempt to load the backtest_start_date from the trades.json file
                trades_filepath = os.path.join(run_path, 'trades.json')
                if os.path.exists(trades_filepath):
                    trades_content = _load_json_file(trades_filepath)
                    if trades_content and 'options' in trades_content and 'start_date' in trades_content['options']:
                        run_data['backtest_start_date'] = trades_content['options']['start_date']

                for date_dir in os.listdir(run_path):
                    date_path = os.path.join(run_path, date_dir)
                    if os.path.isdir(date_path) and os.path.exists(os.path.join(date_path, 'payload.json')):
                        run_data["dates"].append(date_dir)
                run_data["dates"].sort()
                interval_data["runs"].append(run_data)
            if interval_data["runs"]: ticker_data["intervals"].append(interval_data)
        if ticker_data["intervals"]: filters.append(ticker_data)

    return jsonify(filters)

# --- Helper to construct file path ---
def _get_result_filepath(ticker, interval, run_name, filename, daily_date=None):
    """Constructs the full path to a result file."""
    path_parts = [RESULTS_BASE_DIR, ticker, interval, run_name]
    if daily_date:
        path_parts.append(daily_date)
    path_parts.append(filename)
    return os.path.join(*path_parts)

# --- Generic endpoint for fetching run-level data ---
def _fetch_run_level_data(file_type): # Removed backtest_start_date from parameters
    """
    Fetches run-level data (candles, equity, trades) based on query parameters.
    Expected params: ticker, backtest_start_date, interval, run_name.
    """
    ticker = request.args.get('ticker')
    interval = request.args.get('interval')
    run_name = request.args.get('run_name')

    if not all([ticker, interval, run_name]):
        return jsonify({"error": "Missing required parameters: ticker, interval, run_name"}), 400

    filepath = _get_result_filepath(ticker, interval, run_name, f'{file_type}.json')
    data = _load_json_file(filepath)

    if data is None:
        return jsonify({"error": f"{file_type.capitalize()} data not found for the specified run."}), 404
    
    return jsonify(data)

# --- Endpoint: Get Candles ---
@app.route('/candles', methods=['GET'])
def get_candles():
    return _fetch_run_level_data('candles')

# --- Endpoint: Get Equity ---
@app.route('/equity', methods=['GET'])
def get_equity():
    return _fetch_run_level_data('equity')

# --- Endpoint: Get Trades ---
@app.route('/trades', methods=['GET'])
def get_trades():
    return _fetch_run_level_data('trades')

# --- Endpoint: Get Payloads (daily) ---
@app.route('/payloads', methods=['GET'])
def get_payloads():
    """
    Fetches daily payload data based on query parameters.
    Expected params: ticker, backtest_start_date, interval, run_name, date.
    """
    ticker = request.args.get('ticker')
    interval = request.args.get('interval')
    run_name = request.args.get('run_name')
    daily_date = request.args.get('date') # Specific date for the daily payload

    if not all([ticker, interval, run_name, daily_date]):
        return jsonify({"error": "Missing required parameters: ticker, interval, run_name, date"}), 400

    filepath = _get_result_filepath(ticker, interval, run_name, 'payload.json', daily_date=daily_date)
    data = _load_json_file(filepath)

    if data is None:
        return jsonify({"error": "Payload data not found for the specified date and run."}), 404
    
    return jsonify(data)

@app.route('/indicators', methods=['GET'])
def get_indicators():
    """
    Fetches indicators data based on query parameters.
    Expected params: ticker, interval, run_name.
    """
    ticker = request.args.get('ticker')
    interval = request.args.get('interval')
    run_name = request.args.get('run_name')
    key = request.args.get('key')  # Optional key parameter

    if not all([ticker, interval, run_name]):
        return jsonify({"error": "Missing required parameters: ticker, interval, run_name"}), 400

    filepath = _get_result_filepath(ticker, interval, run_name, 'indicators.json')
    data = _load_json_file(filepath)

    if data is None:
        return jsonify({"error": "Indicators data not found for the specified run."}), 404

    if key:
        # Make key lookup case-insensitive
        key_lower = key.lower()
        matched_key = next((k for k in data if k.lower() == key_lower), None)
        if matched_key:
            return jsonify({matched_key: data[matched_key]})
        else:
            return jsonify({"error": f"Indicator key '{key}' not found."}), 404

    return jsonify(data)

# --- Run the Flask app ---
if __name__ == '__main__':
    # Ensure the results directory exists for the server to start
    os.makedirs(RESULTS_BASE_DIR, exist_ok=True)
    logging.info(f"Serving results from: {RESULTS_BASE_DIR}")
    app.run(debug=True, port=5000) # debug=True for development, turn off for production