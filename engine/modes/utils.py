import numpy as np
from typing import List, Tuple
from engine.models.core import Order

# FXBot Candle Indices
# 0: Timestamp
# 1: Open
# 2: High
# 3: Low
# 4: Close
# 5: Volume

def candle_includes_price(candle: np.ndarray, price: float) -> bool:
    return (price >= candle[3]) and (price <= candle[2])

def split_candle(candle: np.ndarray, price: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Splits a candle into two candles based on the price.
    The first candle ends at the price, the second starts at the price.
    """
    # timestamp, open, high, low, close, volume
    
    # First candle (storable)
    c1 = candle.copy()
    c1[4] = price # Close = price
    
    # Adjust High/Low for c1
    # If we are going UP (Open < Close), High should be at least Price
    # If we are going DOWN (Open > Close), Low should be at least Price
    # But actually, we just need to ensure the High/Low range covers the path from Open to Price.
    
    # Simple logic: The path is Open -> Price.
    # So High is max(Open, Price), Low is min(Open, Price)
    # But wait, the original candle might have gone higher/lower before reaching price?
    # We don't know the path inside the candle.
    # Jesse's logic assumes a simple path or uses the original High/Low if they are "on the way".
    
    # Let's stick to a simplified split:
    # c1: Open -> Price
    c1[2] = max(c1[1], price) # High
    c1[3] = min(c1[1], price) # Low
    
    # Second candle (current_temp)
    c2 = candle.copy()
    c2[1] = price # Open = price
    # c2 keeps original High/Low/Close, but we might need to adjust High/Low if they were "consumed" by c1?
    # Actually, if the original High was 110 and we split at 105.
    # c1 (100->105) has High 105.
    # c2 (105->105) has High 110.
    # This seems correct.
    
    return c1, c2

def get_executing_orders(orders: List[Order], candle: np.ndarray) -> List[Order]:
    """
    Returns a list of orders that would be executed within the candle's High/Low range.
    """
    executing_orders = []
    for order in orders:
        if order.status != 'ACTIVE':
            continue
            
        # Check if price is within High/Low
        if candle_includes_price(candle, float(order.price)):
            executing_orders.append(order)
            
    return executing_orders

def sort_execution_orders(orders: List[Order], candle: np.ndarray) -> List[Order]:
    """
    Sorts orders based on execution likelihood within a candle.
    """
    open_price = candle[1]
    close_price = candle[4]
    
    # Split orders into groups
    on_open = []
    above_open = []
    below_open = []
    
    for order in orders:
        p = float(order.price)
        if p == open_price:
            on_open.append(order)
        elif p > open_price:
            above_open.append(order)
        else:
            below_open.append(order)
            
    sorted_orders = []
    sorted_orders.extend(on_open)
    
    is_green = close_price >= open_price
    
    # Heuristic:
    # If Green (Open < Close): Price likely went Down (Low) then Up (High) then Close? 
    # Or Up then Down?
    # Jesse assumes:
    # If Red (Open > Close): Price goes Up then Down.
    # If Green: Price goes Down then Up.
    
    if not is_green: # Red
        # Up then Down
        # Execute above_open (sorted asc), then below_open (sorted desc)
        above_open.sort(key=lambda o: float(o.price))
        below_open.sort(key=lambda o: float(o.price), reverse=True)
        sorted_orders.extend(above_open)
        sorted_orders.extend(below_open)
    else: # Green
        # Down then Up
        # Execute below_open (sorted desc), then above_open (sorted asc)
        below_open.sort(key=lambda o: float(o.price), reverse=True)
        above_open.sort(key=lambda o: float(o.price))
        sorted_orders.extend(below_open)
        sorted_orders.extend(above_open)
        
    return sorted_orders
