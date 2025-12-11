import numpy as np
import pandas as pd
from .utils import closes

def sma(candles, period=14, source_type="close"):
    """
    Simple Moving Average
    """
    if len(candles) == 0:
        return np.array([])
    
    source = closes(candles)
    return pd.Series(source).rolling(window=period).mean().values

def ema(candles, period=14, source_type="close"):
    """
    Exponential Moving Average
    """
    if len(candles) == 0:
        return np.array([])
        
    source = closes(candles)
    return pd.Series(source).ewm(span=period, adjust=False).mean().values
