from engine.strategies.Strategy import Strategy
import engine.indicators as ta

class GoldenCrossStrategy(Strategy):
    """
    Golden Cross Strategy:
    - Buy when 50 SMA crosses above 200 SMA (Golden Cross).
    - Sell when 50 SMA crosses below 200 SMA (Death Cross).
    """
    def __init__(self, symbol, exchange, timeframe, store_instance):
        super().__init__(symbol, exchange, timeframe, store_instance)

    def should_long(self):
        # Need at least 200 candles for the long SMA
        if len(self.candles) < 200:
            return False

        # Calculate Indicators
        sma_50 = ta.sma(self.candles, period=50)
        sma_200 = ta.sma(self.candles, period=200)

        # Check for Crossover (Golden Cross)
        # Current 50 > 200 AND Previous 50 <= 200
        if len(sma_50) > 1 and len(sma_200) > 1:
            curr_50 = sma_50[-1]
            curr_200 = sma_200[-1]
            prev_50 = sma_50[-2]
            prev_200 = sma_200[-2]

            if curr_50 > curr_200 and prev_50 <= prev_200:
                return True
        
        return False

    def should_short(self):
        # Need at least 200 candles
        if len(self.candles) < 200:
            return False

        # Calculate Indicators
        sma_50 = ta.sma(self.candles, period=50)
        sma_200 = ta.sma(self.candles, period=200)

        # Check for Crossunder (Death Cross)
        # Current 50 < 200 AND Previous 50 >= 200
        if len(sma_50) > 1 and len(sma_200) > 1:
            curr_50 = sma_50[-1]
            curr_200 = sma_200[-1]
            prev_50 = sma_50[-2]
            prev_200 = sma_200[-2]

            if curr_50 < curr_200 and prev_50 >= prev_200:
                return True
        
        return False

    def go_long(self):
        # Buy 1.0 unit (or calculate based on balance)
        # For simplicity, we buy 1.0
        qty = 1.0
        self.buy = (qty, self.price)

    def go_short(self):
        # Sell 1.0 unit
        qty = 1.0
        self.sell = (qty, self.price)
