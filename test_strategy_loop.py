import json
import os
import logging
from datetime import datetime, timedelta
from consolidation_breakout import fetch_data, compute_data, generate_payload

def setup_logging(log_file='backtest.log'):
    """Sets up logging to file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a'),
            logging.StreamHandler()
        ]
    )

def get_next_run_dir(base_path):
    """Finds the next available run-X directory."""
    os.makedirs(base_path, exist_ok=True)
    i = 1
    while True:
        run_name = f"run-{i}"
        run_path = os.path.join(base_path, run_name)
        if not os.path.exists(run_path):
            return run_path, run_name
        i += 1


def run_backtest(options=None):
    """
    Iterate through a date range, fetch data for each day,
    compute indicators, generate a payload for the last candle of the day,
    and save it to a file.
    """
    if options is None:
        logging.error("Options were not provided.")
        return
    
    try:
        start_date = datetime.strptime(options['start_date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(options['end_date'], "%Y-%m-%d").date()
        results_file_dir = options.get('results_file_dir')

        current_date = start_date
        while current_date <= end_date:
            logging.info(f"Processing data for {options['ticker']} on {current_date.isoformat()}")

            # Fetch data for the current day
            data = fetch_data(options['ticker'], options['interval'], specific_date=current_date)
            if data.empty:
                logging.warning(f"No data fetched for {current_date.isoformat()}. Skipping.")
                current_date += timedelta(days=1)
                continue

            # --- Efficient Backtesting Logic ---
            # 1. Compute indicators for the entire day's data at once to avoid re-computation in a loop.
            # This is valid because the indicators (SMA, EMA, ADX) are causal and do not "repaint".
            # The result at each row is identical to what it would be in a live, incremental scenario.
            all_computed = compute_data(data, options=options)

            # 2. Iterate through each candle of the day to generate a payload,
            #    simulating how the strategy would have performed tick-by-tick.
            all_payloads = []
            for i in range(len(data)):
                # To simulate the state at candle 'i', pass slices of the dataframes.
                # generate_payload uses the last row of the data it receives.
                data_slice = data.iloc[:i+1]
                computed_slice = all_computed.iloc[:i+1]
                
                payload = generate_payload(data_slice, computed_slice, options=options)
                all_payloads.append(json.loads(payload))

            # 3. Save the results for the processed day.
            if results_file_dir:
                try:
                    # Structure the output to include options and payloads
                    output_data = {
                        "options": options,
                        "payloads": all_payloads
                    }
                    # Save the structured data to a JSON file for the current date.
                    # The filename should reflect the date the data is FOR.
                    filename = f'{options["ticker"]}_{current_date.strftime("%Y-%m-%d")}.json'
                    results_filepath = os.path.join(results_file_dir, filename)
                    with open(results_filepath, 'w') as f:
                        json.dump(output_data, f, indent=4)
                    logging.info(f"Saved run to {results_filepath}")
                except Exception as e:
                    logging.error(f"Error saving results file: {e}")
            current_date += timedelta(days=1)

    except Exception as e:
        logging.error(f"An error occurred during the backtest: {e}", exc_info=True)
    

if __name__ == "__main__":
    # Base options for the backtest
    options = {
        "start_date": "2025-10-13",
        "end_date": "2025-10-17",
        "interval": "5m",
        "ticker": "EURUSD=X",
        "save_location_base": "test_results", # Root directory for all results
        'ema_short': 8,           # Scalpy fast EMA
        'ema_long': 34,           # Fib-tuned slow
        'window': 20,             # Tighter BB
        'threshold_bb': 0.7,      # Looser range filter
        'threshold_adx': 20,      # Sub-weak trend
        'tolerance': 0.4,         # Snug BB deviation
        'loops': 3,               # More gap-filling iterations
    }

    # --- Create dynamic run directory (e.g., run-1, run-2) ---
    base_run_path = os.path.join(
        options['save_location_base'],
        options['ticker'],
        options['interval']
    )
    output_dir, run_name = get_next_run_dir(base_run_path)
    os.makedirs(output_dir, exist_ok=True)

    # --- Setup logging and results file paths inside the run directory ---
    log_file_path = os.path.join(output_dir, f'{run_name}.log')
    results_filepath = os.path.join(output_dir, f'{run_name}.json')
    options['results_file_dir'] = output_dir

    setup_logging(log_file=log_file_path)

    run_backtest(options=options)
