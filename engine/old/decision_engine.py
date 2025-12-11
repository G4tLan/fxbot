import logging
from old.decision_strategies import BaseDecisionStrategy

class DecisionEngine:
    """
    A factory for creating and retrieving strategy-specific decision objects.
    It "lazily" instantiates a strategy class only when it's requested.
    """
    def __init__(self):
        self._strategies = {}

    def register_strategy(self, name: str, strategy_class):
        logging.info(f"Registering strategy: {name}")
        self._strategies[name] = strategy_class

    def get_strategy(self, name: str) -> BaseDecisionStrategy | None:
        strategy_class = self._strategies.get(name)
        if strategy_class:
            # "Lazy loading": we only create an instance when it's requested.
            return strategy_class()
        logging.warning(f"No strategy registered with the name: {name}")
        return None

    def run_strategy(self, name: str, payload: dict, options: dict = None) -> dict:
        strategy_handler = self.get_strategy(name)
        if strategy_handler:
            decision = strategy_handler.evaluate(payload, options)
            return decision
