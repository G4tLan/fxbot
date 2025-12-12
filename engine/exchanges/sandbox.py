from engine.exchanges.exchange import Exchange
from engine.models.core import Order
import uuid
import time

class Sandbox(Exchange):
    def __init__(self, store_instance, log_func=print):
        super().__init__('Sandbox')
        self.store = store_instance
        self.log = log_func

    def fetch_ohlcv(self, symbol, timeframe, start_ts, end_ts=None):
        return []

    def market_order(self, symbol: str, qty: float, current_price: float, side: str, reduce_only: bool = False) -> Order:
        order = Order(
            id=str(uuid.uuid4()),
            symbol=symbol,
            exchange=self.name,
            side=side,
            type='MARKET',
            qty=qty,
            price=current_price,
            status='ACTIVE',
            submitted_at=int(time.time() * 1000),
            reduce_only=reduce_only
        )
        
        self.store.orders.append(order)
        return order

    def limit_order(self, symbol: str, qty: float, price: float, side: str, reduce_only: bool = False) -> Order:
        order = Order(
            id=str(uuid.uuid4()),
            symbol=symbol,
            exchange=self.name,
            side=side,
            type='LIMIT',
            qty=qty,
            price=price,
            status='ACTIVE',
            submitted_at=int(time.time() * 1000),
            reduce_only=reduce_only
        )
        
        self.store.orders.append(order)
        return order

    def stop_order(self, symbol: str, qty: float, price: float, side: str, reduce_only: bool = False) -> Order:
        order = Order(
            id=str(uuid.uuid4()),
            symbol=symbol,
            exchange=self.name,
            side=side,
            type='STOP',
            qty=qty,
            price=price,
            status='ACTIVE',
            submitted_at=int(time.time() * 1000),
            reduce_only=reduce_only
        )
        
        self.store.orders.append(order)
        return order

    def cancel_all_orders(self, symbol: str) -> None:
        for order in self.store.orders:
            if order.symbol == symbol and order.status == 'ACTIVE':
                order.status = 'CANCELED'

    def cancel_order(self, symbol: str, order_id: str) -> None:
        for order in self.store.orders:
            if order.symbol == symbol and order.id == order_id:
                order.status = 'CANCELED'
                break

    def _fetch_precisions(self) -> None:
        pass

    def execute_order(self, order: Order):
        # 1. Update Status
        order.status = 'EXECUTED'
        # Use store time if available, else system time
        if self.store.current_candle is not None:
            order.executed_at = self.store.current_candle[0]
        else:
            order.executed_at = int(time.time() * 1000)
        
        # 2. Update Store (Balance & Position)
        key = f"{self.name}-{order.symbol}"
        if key not in self.store.positions:
            self.store.positions[key] = {'qty': 0, 'entry_price': 0, 'opened_at': 0}
        
        position = self.store.positions[key]
        current_qty = float(position['qty'])
        current_entry = float(position['entry_price'])
        
        qty = float(order.qty)
        price = float(order.price)
        
        cost = qty * price
        # Default fee rate if not set
        if not hasattr(self, 'fee_rate'): self.fee_rate = 0.001
        fee = cost * self.fee_rate
        
        if self.name not in self.store.balance:
            self.store.balance[self.name] = 10000
            
        # Update Cash Balance
        if order.side == 'buy':
            self.store.balance[self.name] -= (cost + fee)
        elif order.side == 'sell':
            self.store.balance[self.name] += (cost - fee)

        # Update Position & Track Closed Trades
        if order.side == 'buy':
            # BUYING
            if current_qty < 0: # We are Short
                # Covering
                qty_covered = min(abs(current_qty), qty)
                
                # Record Closed Trade (Short)
                pnl = (current_entry - price) * qty_covered
                self.store.closed_trades.append({
                    'entry_price': current_entry,
                    'exit_price': price,
                    'qty': qty_covered,
                    'pnl': pnl,
                    'opened_at': position.get('opened_at', order.executed_at),
                    'closed_at': order.executed_at,
                    'strategy_name': 'SimpleStrategy',
                    'leverage': 1,
                    'type': 'short'
                })
                
                if qty > abs(current_qty): # Flipping to Long
                    qty_new_long = qty - abs(current_qty)
                    position['qty'] = qty_new_long
                    position['entry_price'] = price
                    position['opened_at'] = order.executed_at
                else: # Reducing Short or Closing Flat
                    position['qty'] = current_qty + qty # e.g. -10 + 5 = -5
                    if position['qty'] == 0:
                        position['entry_price'] = 0
                        position['opened_at'] = 0
                        
            else: # We are Long or Flat
                # Adding to Long
                new_qty = current_qty + qty
                if current_qty == 0:
                    position['entry_price'] = price
                    position['opened_at'] = order.executed_at
                else:
                    # Weighted Average Entry
                    position['entry_price'] = ((current_qty * current_entry) + (qty * price)) / new_qty
                
                position['qty'] = new_qty

        elif order.side == 'sell':
            # SELLING
            if current_qty > 0: # We are Long
                # Closing
                qty_closed = min(current_qty, qty)
                
                # Record Closed Trade (Long)
                pnl = (price - current_entry) * qty_closed
                self.store.closed_trades.append({
                    'entry_price': current_entry,
                    'exit_price': price,
                    'qty': qty_closed,
                    'pnl': pnl,
                    'opened_at': position.get('opened_at', order.executed_at),
                    'closed_at': order.executed_at,
                    'strategy_name': 'SimpleStrategy',
                    'leverage': 1,
                    'type': 'long'
                })
                
                if qty > current_qty: # Flipping to Short
                    qty_new_short = qty - current_qty
                    position['qty'] = -qty_new_short
                    position['entry_price'] = price
                    position['opened_at'] = order.executed_at
                else: # Reducing Long or Closing Flat
                    position['qty'] = current_qty - qty
                    if position['qty'] == 0:
                        position['entry_price'] = 0
                        position['opened_at'] = 0
            
            else: # We are Short or Flat
                # Adding to Short
                new_qty = abs(current_qty) + qty
                if current_qty == 0:
                    position['entry_price'] = price
                    position['opened_at'] = order.executed_at
                else:
                    # Weighted Average Entry
                    position['entry_price'] = ((abs(current_qty) * current_entry) + (qty * price)) / new_qty
                
                position['qty'] = -new_qty

        # 3. Log Trade
        trade_record = {
            'timestamp': order.executed_at,
            'symbol': order.symbol,
            'side': order.side,
            'qty': qty,
            'price': price,
            'fee': fee,
            'type': order.type
        }
        self.store.trades.append(trade_record)
        self.log(f"[Sandbox] EXECUTED {order.side} {qty} {order.symbol} @ {price}")
