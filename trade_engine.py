import pandas as pd
import uuid
import logging
from datetime import datetime

class TradeEngine:
    """
    A class to simulate a trading engine, managing candles, active trades,
    closed trades, and an account balance.
    """

    def __init__(self, initial_account_amount: float = 10000.0, risk_percentage: float = 0.01, leverage: int = 30):
        """
        Initializes the TradeEngine with an empty candle database,
        empty trade lists, and an initial account balance.
        """
        self._initial_balance = initial_account_amount

        # 1. Database for all candles
        self._candle_data = pd.DataFrame(
            columns=['datetime', 'High', 'Low', 'Close', 'Open', 'Volume']
        ).set_index('datetime')
        self._candle_data.index = pd.to_datetime(self._candle_data.index)

        # 2. DataFrames for active and closed trades
        self._active_trades = pd.DataFrame(
            columns=[
                'entry_id', 'ticker', 'entry_datetime', 'entry_price', 'type',
                'stop_loss', 'take_profit', 'size_units', 'margin_used', 'status'
            ]
        ).set_index('entry_id')

        self._closed_trades = pd.DataFrame(
            columns=[
                'entry_id', 'ticker', 'entry_datetime', 'entry_price', 'type',
                'stop_loss', 'take_profit', 'size_units', 'margin_used',
                'closed_datetime', 'closed_price', 'profit'
            ]
        ).set_index('entry_id')

        # 3. Account balance
        self._account_amount = initial_account_amount
        self._risk_percentage = risk_percentage
        self._leverage = leverage
        logging.info(f"TradeEngine initialized with account balance: {self._account_amount:.2f}")

    def add_candle(self, candle_row: pd.Series):
        """
        Adds a new candle to the internal database and checks for SL/TP hits
        on active trades.

        Args:
            candle_row (pd.Series): A single row DataFrame (or Series) representing a candle.
                                    Expected columns: datetime (index), High, Low, Close, Open, Volume.
        """
        if not isinstance(candle_row.name, pd.Timestamp):
            raise ValueError("Candle row must have a datetime index.")

        # Ensure the candle_row is a Series with a name (datetime index)
        if isinstance(candle_row, pd.DataFrame):
            if len(candle_row) != 1:
                raise ValueError("add_candle expects a single candle row.")
            candle_row = candle_row.iloc[0]

        self._candle_data.loc[candle_row.name] = candle_row
        logging.debug(f"Candle added: {candle_row.name} - Close: {candle_row['Close']:.5f}")

        self._check_sl_tp_hits(candle_row)

    def _check_sl_tp_hits(self, current_candle: pd.Series):
        """
        Checks all active trades against the current candle's High/Low/Close
        to see if Stop Loss or Take Profit levels have been hit.
        Prioritizes Stop Loss over Take Profit if both are hit in the same candle.
        """
        trades_to_close = []

        for entry_id, trade in self._active_trades.iterrows():
            close_price = None
            reason = None

            # Check Stop Loss first
            if trade['type'] == 'BUY':
                if current_candle['Low'] <= trade['stop_loss']:
                    close_price = trade['stop_loss']
                    reason = "Stop Loss hit (BUY)"
            elif trade['type'] == 'SELL':
                if current_candle['High'] >= trade['stop_loss']:
                    close_price = trade['stop_loss']
                    reason = "Stop Loss hit (SELL)"

            # If SL not hit, check Take Profit
            if close_price is None and pd.notna(trade['take_profit']):
                if trade['type'] == 'BUY':
                    if current_candle['High'] >= trade['take_profit']:
                        close_price = trade['take_profit']
                        reason = "Take Profit hit (BUY)"
                elif trade['type'] == 'SELL':
                    if current_candle['Low'] <= trade['take_profit']:
                        close_price = trade['take_profit']
                        reason = "Take Profit hit (SELL)"
            
            # If neither SL nor TP hit, but the candle's close crosses SL/TP,
            # it's a less precise but still valid check for backtesting.
            # This part is optional depending on desired precision.
            if close_price is None:
                if trade['type'] == 'BUY':
                    if current_candle['Close'] <= trade['stop_loss']:
                        close_price = trade['stop_loss'] # Or current_candle['Close']
                        reason = "Stop Loss hit (BUY - close price)"
                    elif pd.notna(trade['take_profit']) and current_candle['Close'] >= trade['take_profit']:
                        close_price = trade['take_profit'] # Or current_candle['Close']
                        reason = "Take Profit hit (BUY - close price)"
                elif trade['type'] == 'SELL':
                    if current_candle['Close'] >= trade['stop_loss']:
                        close_price = trade['stop_loss'] # Or current_candle['Close']
                        reason = "Stop Loss hit (SELL - close price)"
                    elif pd.notna(trade['take_profit']) and current_candle['Close'] <= trade['take_profit']:
                        close_price = trade['take_profit'] # Or current_candle['Close']
                        reason = "Take Profit hit (SELL - close price)"

            if close_price is not None:
                trades_to_close.append((entry_id, close_price, current_candle.name, reason))

        for entry_id, close_price, close_datetime, reason in trades_to_close:
            self._exit_trade(entry_id, close_price, close_datetime, reason)

    def execute_trade(self, trade_details: dict) -> str | None:
        """
        Executes a new trade and adds it to the active trades.

        Args:
            trade_details (dict): Dictionary containing trade parameters:
                                  {"entry_price": float, "type": "BUY"|"SELL",
                                   "stop_loss": float, "take_profit": float (optional),
                                   "datetime": datetime, "ticker": str}

        Returns:
            str | None: The entry_id of the new trade if successful, None otherwise.
        """
        # Ensure datetime is a proper datetime object before proceeding.
        execution_dt = trade_details.get('datetime')
        if isinstance(execution_dt, str):
            try:
                execution_dt = datetime.fromisoformat(execution_dt)
            except (ValueError, TypeError):
                logging.error(f"Invalid datetime string format in trade_details: {execution_dt}")
                return None

        latest_candle_time = self._candle_data.index.max()
        if latest_candle_time is None: # Handle case where no candles are added yet
            logging.warning("No candles available in TradeEngine. Cannot execute trade.")
            return None

        if execution_dt.timestamp() != latest_candle_time.timestamp():
            logging.warning(
                f"Trade execution time {execution_dt} (timestamp: {execution_dt.timestamp()}) does not match "
                f"latest candle time {latest_candle_time} (timestamp: {latest_candle_time.timestamp()}). Trade not executed."
            )
            return None

        # --- Position Sizing and Margin Calculation ---
        amount_to_risk = self._account_amount * self._risk_percentage
        stop_loss_pips = abs(trade_details['entry_price'] - trade_details['stop_loss'])

        if stop_loss_pips == 0:
            logging.warning("Stop loss cannot be zero. Trade not executed.")
            return None

        # Assuming 1 unit of currency (e.g., for EUR/USD, 1 EUR).
        # A more complex implementation would use pip value based on the pair.
        # For simplicity, we treat the price difference directly as the loss per unit.
        position_size_units = amount_to_risk / stop_loss_pips

        # Calculate margin required for the position
        notional_value = position_size_units * trade_details['entry_price']
        margin_required = notional_value / self._leverage

        # Check if there is enough equity for the margin
        # A more complex model would use Free Margin = Equity - Used Margin
        if margin_required > self._account_amount:
            logging.warning(
                f"Insufficient margin to execute trade. "
                f"Required: {margin_required:.2f}, Available: {self._account_amount:.2f}"
            )
            return None

        entry_id = str(uuid.uuid4())
        new_trade = {
            'entry_id': entry_id,
            'ticker': trade_details['ticker'],
            'entry_datetime': execution_dt,
            'entry_price': trade_details['entry_price'],
            'type': trade_details['type'],
            'stop_loss': trade_details['stop_loss'],
            'take_profit': trade_details['take_profit'] if 'take_profit' in trade_details else None,
            'size_units': position_size_units,
            'margin_used': margin_required,
            'status': 'ACTIVE'
        }
        self._active_trades.loc[entry_id] = new_trade
        logging.info(
            f"Trade {entry_id} executed: {new_trade['type']} {new_trade['size_units']:.2f} units of "
            f"{new_trade['ticker']} @ {new_trade['entry_price']:.5f}. Margin used: {margin_required:.2f}"
        )
        return entry_id

    def _exit_trade(self, entry_id: str, close_price: float, close_datetime: datetime, reason: str = "Manual Close") -> bool:
        """
        Closes an active trade, calculates profit, and updates the account balance.

        Args:
            entry_id (str): The ID of the trade to close.
            close_price (float): The price at which the trade is closed.
            close_datetime (datetime): The datetime of the closure.
            reason (str): The reason for closing the trade (e.g., "SL hit", "TP hit", "Manual Close").

        Returns:
            bool: True if the trade was successfully closed, False otherwise.
        """
        if entry_id not in self._active_trades.index:
            logging.warning(f"Attempted to close non-existent or already closed trade: {entry_id}")
            return False

        trade = self._active_trades.loc[entry_id].copy()
        
        # Calculate profit/loss based on position size
        price_difference = close_price - trade['entry_price']
        if trade['type'] == 'BUY':
            profit = price_difference * trade['size_units']
        else:  # SELL
            profit = -price_difference * trade['size_units']

        # Update account balance
        self._account_amount += profit

        # Move trade to closed_trades
        closed_trade_data = trade.to_dict()
        closed_trade_data.update({
            'closed_datetime': close_datetime,
            'closed_price': close_price,
            'profit': profit,
            'status': 'CLOSED',
            'reason': reason # Add reason for closure
        })
        self._closed_trades.loc[entry_id] = closed_trade_data

        # Remove from active trades
        self._active_trades.drop(index=entry_id, inplace=True)

        logging.info(
            f"Trade {entry_id} closed ({reason}): {trade['type']} {trade['ticker']} "
            f"Entry @ {trade['entry_price']:.5f}, Close @ {close_price:.5f}. "
            f"Profit: {profit:.2f}. New Balance: {self._account_amount:.2f}"
        )
        return True

    def close_trade(self, entry_id: str, reason: str = "Manual Close") -> bool:
        """
        Closes an active trade at the latest available candle's close price.

        Args:
            entry_id (str): The ID of the trade to close.
            reason (str): The reason for closing the trade (e.g., "Manual Close", "Strategy Exit").

        Returns:
            bool: True if the trade was successfully closed, False otherwise.
        """
        if self._candle_data.empty:
            logging.warning(f"Cannot close trade {entry_id}: No candle data available to determine close price.")
            return False

        latest_candle_time = self._candle_data.index.max()
        if latest_candle_time is None:
            logging.warning(f"Cannot close trade {entry_id}: No latest candle time found.")
            return False
            
        close_price = self._candle_data.loc[latest_candle_time]['Close']
        
        return self._exit_trade(entry_id, close_price, latest_candle_time, reason)

    def get_account_balance(self) -> float:
        """Returns the current account balance."""
        return self._account_amount

    def _calculate_unrealised_pnl(self) -> float:
        """
        Calculates the total unrealised profit or loss for all active trades
        based on the latest available candle's close price.
        """
        if self._active_trades.empty or self._candle_data.empty:
            return 0.0

        latest_candle_time = self._candle_data.index.max()
        current_price = self._candle_data.loc[latest_candle_time]['Close']
        
        unrealised_pnl = 0.0
        for _, trade in self._active_trades.iterrows():
            price_difference = current_price - trade['entry_price']
            if trade['type'] == 'BUY':
                pnl = price_difference * trade['size_units']
            else:  # SELL
                pnl = -price_difference * trade['size_units']
            unrealised_pnl += pnl
        
        return unrealised_pnl

    def get_account_equity(self) -> float:
        """
        Returns the current account equity (balance + unrealised P/L).
        This is the true current value of the account.
        """
        return self._account_amount + self._calculate_unrealised_pnl()

    def get_candle_data(self) -> list[dict]:
        """Returns all processed candle data as a list of dictionaries."""
        # The index is the datetime, so we need to reset it to include it in the dict.
        return self._candle_data.reset_index().to_dict(orient='records')

    def get_active_trades(self, include_pnl: bool = False, **filters) -> list[dict]:
        """
        Returns a list of active trades as dictionaries, with optional filtering.

        Args:
            **filters: Keyword arguments to filter trades by.
                       Example: get_active_trades(ticker="EURUSD=X", type="BUY")

            include_pnl (bool): If True, includes the current unrealised P/L for each trade.

        Returns:
            list[dict]: A list of active trades matching the filters.
        """
        filtered_trades = self._active_trades
        if filters:
            for key, value in filters.items():
                if key in filtered_trades.columns:
                    filtered_trades = filtered_trades[filtered_trades[key] == value]
                else:
                    logging.warning(f"Invalid filter key '{key}' for get_active_trades. Ignoring.")
        
        trades_list = filtered_trades.reset_index().to_dict(orient='records')

        if include_pnl and not self._candle_data.empty:
            latest_candle_time = self._candle_data.index.max()
            current_price = self._candle_data.loc[latest_candle_time]['Close']
            
            for trade in trades_list:
                price_difference = current_price - trade['entry_price']
                if trade['type'] == 'BUY':
                    pnl = price_difference * trade['size_units']
                else: # SELL
                    pnl = -price_difference * trade['size_units']
                trade['unrealised_pnl'] = pnl
        elif include_pnl:
            for trade in trades_list:
                trade['unrealised_pnl'] = 0.0

        return trades_list

    def get_closed_trades(self) -> list[dict]:
        """Returns a list of closed trades as dictionaries."""
        return self._closed_trades.reset_index().to_dict(orient='records')

    def get_historical_trades(self) -> list[dict]:
        """
        Returns a list of dictionaries, each containing details of a closed trade
        along with its original entry parameters.
        """
        historical_trades = []
        for entry_id, closed_trade in self._closed_trades.iterrows():
            # The closed_trade already contains all entry details as well
            historical_trades.append(closed_trade.to_dict())
        return historical_trades