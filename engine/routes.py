from typing import Dict, Type
from engine.strategies.Strategy import Strategy

class Router:
    def __init__(self):
        self.routes: Dict[str, Type[Strategy]] = {}

    def register(self, exchange: str, symbol: str, timeframe: str, strategy_class: Type[Strategy]):
        """
        Register a strategy for a specific route.
        """
        key = f"{exchange}-{symbol}-{timeframe}"
        self.routes[key] = strategy_class

    def get_strategy(self, exchange: str, symbol: str, timeframe: str) -> Type[Strategy]:
        """
        Retrieve the strategy class for a specific route.
        """
        key = f"{exchange}-{symbol}-{timeframe}"
        return self.routes.get(key)

router = Router()
