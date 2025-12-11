import numpy as np
import pandas as pd
from .utils import closes

def rsi(candles, period=14, source_type="close"):
    """
    Relative Strength Index
    """
    if len(candles) == 0:
        return np.array([])
        
    source = closes(candles)
    series = pd.Series(source)
    delta = series.diff()
    
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    
    # Wilder's Smoothing (alpha = 1/n) which corresponds to com = n - 1
    avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.fillna(0).values
