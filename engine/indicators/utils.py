import numpy as np

def opens(candles):
    return candles[:, 1].astype(float)

def highs(candles):
    return candles[:, 2].astype(float)

def lows(candles):
    return candles[:, 3].astype(float)

def closes(candles):
    return candles[:, 4].astype(float)

def volumes(candles):
    return candles[:, 5].astype(float)
