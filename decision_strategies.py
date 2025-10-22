from abc import ABC, abstractmethod
import logging

class BaseDecisionStrategy(ABC):
    """
    Abstract base class for all trading decision strategies.
    Ensures that any new strategy implements the 'evaluate' method.
    """
    @abstractmethod
    def evaluate(self, payload: dict, options: dict = None) -> dict:
        """
        Evaluates a given payload and returns a decision.

        Args:
            payload (dict): The data payload from the analysis script.
            options (dict, optional): Strategy options, like 'window'. Defaults to None.

        Returns:
            dict: A dictionary containing the action taken and entry details if applicable.
        """
        pass

class ConsolidationBreakoutStrategy(BaseDecisionStrategy):
    """
    Decision logic for the 'consolidation_breakout' strategy.
    
    TODO: Implement the actual decision-making logic here.
    """
    def evaluate(self, payload: dict, options: dict = None) -> dict:
        """
        Implements the decision logic based on the fx_decision_tree.drawio.xml diagram.
        """
        if options is None:
            options = {}

        conditions = payload.get("conditions", {})
        candle = payload.get("candle", {})
        window = options.get('window', 25) # Default window if not provided

        # Node 1: Is trend_status 'consolidating'?
        if conditions.get("trend_status") == "consolidating":
            return {"action_taken": "NO_ACTION", "reason": "Market is in consolidation."}

        # Node 2: Is there an EMA crossover?
        ema_crossover = conditions.get("ema_crossover")
        if ema_crossover != "none":
            return {
                "action_taken": "CLOSE_ENTRY",
                "reason": f"EMA crossover detected ({ema_crossover}). Signal to close existing positions.",
                "entry": {
                    "type": "CLOSE"
                }
            }

        # Node 3: Are we in the immediate aftermath of a consolidation?
        # (candles_since_consolidation > 0 ensures we are not *in* consolidation)
        candles_since = conditions.get("candles_since_consolidation", float('inf'))
        if not (0 < candles_since < window):
            return {"action_taken": "NO_ACTION", "reason": f"Not within breakout window ({candles_since} candles since consolidation)."}

        # Node 4: Is the breakout happening shortly after a crossover?
        candles_since_crossover = conditions.get("candles_since_crossover", float('inf'))
        crossover_window = 0.25 * window
        if candles_since_crossover >= crossover_window:
            return {"action_taken": "NO_ACTION", "reason": f"Breakout is not recent enough to a crossover ({candles_since_crossover} candles ago)."}

        # Node 5 & 6: Bullish breakout check
        if conditions.get("trend_status") == "bullish":
            if candle.get("close", 0) > conditions.get("consolidation_maxima", float('inf')):
                price = candle.get("close")
                stop_loss = conditions.get("consolidation_minima")
                return {
                    "action_taken": "BUY_ENTRY",
                    "reason": "Bullish breakout above consolidation maxima.",
                    "entry": {
                        "entry_price": price,
                        "type": "BUY",
                        "stop_loss": stop_loss,
                        "ticker": payload.get("ticker", None),
                        "datetime": payload.get("datetime", None)
                    }
                }

        # Node 5 & 7: Bearish breakout check
        if conditions.get("trend_status") == "bearish":
            if candle.get("close", 0) < conditions.get("consolidation_minima", 0):
                price = candle.get("close")
                stop_loss = conditions.get("consolidation_maxima")
                return {
                    "action_taken": "SELL_ENTRY",
                    "reason": "Bearish breakdown below consolidation minima.",
                    "entry": {
                        "entry_price": price,
                        "type": "SELL",
                        "stop_loss": stop_loss,
                        "ticker": payload.get("ticker", None),
                        "datetime": payload.get("datetime", None)
                    }
                }

        return {"action_taken": "NO_ACTION", "reason": "Conditions for entry not met."}
