import time
import requests
import json
import logging
from datetime import datetime
from old.consolidation_breakout import fetch_data, compute_data, generate_payload

def setup_logging(log_file='strategy_loop.log'):
    """Sets up logging to file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a'),
            logging.StreamHandler()
        ]
    )

def run_strategy_incremental(options=None):
    """
    Continuously fetch the latest candle every interval, 
    keep accumulating data, compute indicators incrementally,
    and post payloads.
    """
    if options is None:
        logging.error("Options were not provided.")
        return
    
    all_data = None        # full OHLCV dataframe
    all_computed = None    # full indicators dataframe
    last_timestamp = None
    
    while True:
        try:
            now = datetime.now(datetime.timezone.utc)
            logging.info(f"Fetching latest data for {options['ticker']}...")

            # Fetch the latest candle
            data = fetch_data(options['ticker'], options['interval'], specific_date=now.date())
            if data.empty:
                logging.warning("No data fetched. Retrying in 5 minutes.")
                time.sleep(300)
                continue # restart loop

            # Only keep new rows we haven't processed yet
            if last_timestamp is not None:
                data = data[data.index > last_timestamp]
                if data.empty:
                    logging.info("No new candles to process. Sleeping for 5 minutes.")
                    time.sleep(300)
                    continue

            # Append to cumulative dataset
            if all_data is None:
                all_data = data
            else:
                all_data = all_data.append(data)

            # Recompute indicators for the full dataset
            all_computed = compute_data(all_data, options=options)

            # Generate payloads for only the new rows
            for row_index in range(len(all_data) - len(data), len(all_data)):
                payload = generate_payload(all_data, all_computed, row_index=row_index, options=options)
                if options['post_url']:
                    try:
                        response = requests.post(options['post_url'], json=payload)
                        logging.info(f"Posted payload for {all_data.index[row_index]}, status: {response.status_code}")
                    except Exception as e:
                        logging.error(f"Error posting payload: {e}")
                else:
                    logging.info(f"Generated payload (no post_url):\n{json.dumps(payload, indent=4)}")
                
                last_timestamp = all_data.index[row_index]

        except Exception as e:
            logging.error(f"Error in strategy loop: {e}", exc_info=True)

        logging.info("Sleeping for 5 minutes...\n")
        time.sleep(300)  # sleep 5 minutes

if __name__ == "__main__":
    setup_logging()
    run_strategy_incremental(
        options={
            "window": 25, 
            "ema_short": 9, 
            "ema_long": 21, 
            "interval": "5m",
            "ticker": "AAPL",
            "post_url":"https://your-endpoint.com/api/payload"
        },
    )
