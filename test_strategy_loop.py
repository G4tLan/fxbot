import json
import os
import logging
from datetime import datetime, timedelta
from consolidation_breakout import fetch_data, compute_data, generate_payload
import pandas as pd
from decision_engine import DecisionEngine
from decision_strategies import ConsolidationBreakoutStrategy
from trade_engine import TradeEngine

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

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    raise TypeError (f"Type {type(obj)} not serializable")


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
        engine = DecisionEngine()
        engine.register_strategy("consolidation_breakout", ConsolidationBreakoutStrategy)
        trade_engine = TradeEngine()

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
                trade_engine.add_candle(data_slice.iloc[-1])
                
                payload = generate_payload(data_slice, computed_slice, options=options)
                decision = engine.run_strategy(payload.get('strategy_type'), payload, options)

                if decision:
                    if decision.get('action_taken') == 'BUY_ENTRY' or decision.get('action_taken') == 'SELL_ENTRY':
                        trade_engine.execute_trade(decision.get('entry'))
                    elif decision.get('action_taken') == 'CLOSE_ENTRY':
                        # A crossover signals an exit. Close trades against the new trend direction.
                        ema_crossover = payload.get('conditions', {}).get('ema_crossover')
                        if ema_crossover == 'bullish': # Bullish crossover, close any open SELL trades
                            for trade in trade_engine.get_active_trades(type='SELL'):
                                trade_engine.close_trade(trade['entry_id'], reason="Strategy Exit: Bullish Crossover")
                        elif ema_crossover == 'bearish': # Bearish crossover, close any open BUY trades
                            for trade in trade_engine.get_active_trades(type='BUY'):
                                trade_engine.close_trade(trade['entry_id'], reason="Strategy Exit: Bearish Crossover")
                
                # Combine the payload and its corresponding decision into a single record
                record = json.loads(json.dumps({"payload": payload, "decision": decision}, indent=4))
                all_payloads.append(record)

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
    finally:
        # --- Save Final Trade Summary and Candle Data ---
        if 'trade_engine' in locals() and results_file_dir:
            logging.info("Saving final backtest results...")
            try:
                run_name = os.path.basename(results_file_dir)

                # Save Trade Summary
                trades_summary_filepath = os.path.join(results_file_dir, f'{run_name}_trades.json')
                summary_data = {
                    "active_trades": trade_engine.get_active_trades(include_pnl=True),
                    "closed_trades": trade_engine.get_closed_trades(),
                    "final_balance": trade_engine.get_account_balance()
                }
                with open(trades_summary_filepath, 'w') as f:
                    json.dump(summary_data, f, indent=4, default=json_serial)
                logging.info(f"Successfully saved trade summary to {trades_summary_filepath}")

                # Save Candle Data
                candles_filepath = os.path.join(results_file_dir, f'{run_name}_candles.json')
                candle_data = trade_engine.get_candle_data()
                with open(candles_filepath, 'w') as f:
                    json.dump(candle_data, f, indent=4, default=json_serial)
                logging.info(f"Successfully saved candle data to {candles_filepath}")
                
            except Exception as e:
                logging.error(f"Could not save final backtest results: {e}", exc_info=True)
    

if __name__ == "__main__":
    # Base options for the backtest
    options = {
        "start_date": "2025-10-20",
        "end_date": "2025-10-20",
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
