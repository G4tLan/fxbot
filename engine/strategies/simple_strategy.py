from engine.strategies.Strategy import Strategy

class SimpleStrategy(Strategy):
    def __init__(self, symbol, exchange, timeframe, store_instance):
        super().__init__(symbol, exchange, timeframe, store_instance)

    def should_long(self):
        # Simple logic: Buy if price drops 3 candles in a row
        if len(self.candles) < 3:
            return False
            
        c1 = self.candles[-1][4]
        c2 = self.candles[-2][4]
        c3 = self.candles[-3][4]
        
        if c1 < c2 and c2 < c3:
            return True
        return False

    def go_long(self):
        self.buy = (1.0, self.price)
