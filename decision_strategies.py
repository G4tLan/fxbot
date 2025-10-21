from abc import ABC, abstractmethod
import logging

class BaseDecisionStrategy(ABC):
    """
    Abstract base class for all trading decision strategies.
    Ensures that any new strategy implements the 'evaluate' method.
    """
    @abstractmethod
    def evaluate(self, payload: dict) -> dict:
        """
        Evaluates a given payload and returns a decision.

        Args:
            payload (dict): The data payload from the analysis script.

        Returns:
            dict: A dictionary containing the decision (e.g., 'BUY', 'SELL', 'HOLD')
                  and the reasoning behind it.
        """
        pass

class ConsolidationBreakoutStrategy(BaseDecisionStrategy):
    """
    Decision logic for the 'consolidation_breakout' strategy.
    
    TODO: Implement the actual decision-making logic here.
    """
    def evaluate(self, payload: dict) -> dict:
        # Placeholder logic. This is where you will build your decision tree.
        logging.info(f"Evaluating payload for strategy: {payload.get('strategy_type')}")
        
        conditions = payload.get("conditions", {})
        candle = payload.get("candle", {})

        # Example of a simple rule:
        # If the trend is bullish and we just broke above the consolidation maxima, consider a BUY.
        if (conditions.get("trend_status") == "bullish" and 
            conditions.get("candles_since_consolidation") > 0 and
            candle.get("close", 0) > conditions.get("consolidation_maxima", float('inf'))):
            
            return {"action": "BUY", "reason": "Breakout above consolidation maxima in a bullish trend."}

        # Another example rule:
        # If the trend is bearish and we just broke below the consolidation minima, consider a SELL.
        if (conditions.get("trend_status") == "bearish" and 
            conditions.get("candles_since_consolidation") > 0 and
            candle.get("close", 0) < conditions.get("consolidation_minima", 0)):
            
            return {"action": "SELL", "reason": "Breakdown below consolidation minima in a bearish trend."}

        return {"action": "HOLD", "reason": "No breakout signal detected."}
