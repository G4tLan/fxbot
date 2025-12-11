from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from engine.modes.backtest_mode import run_backtest
from engine.strategies.simple_strategy import SimpleStrategy

router = APIRouter()

class BacktestRequest(BaseModel):
    exchange: str
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    strategy_name: str

STRATEGIES = {
    "SimpleStrategy": SimpleStrategy
}

@router.post("/backtest")
async def trigger_backtest(request: BacktestRequest):
    """
    Run a backtest synchronously and return results.
    """
    strategy_class = STRATEGIES.get(request.strategy_name)
    if not strategy_class:
        raise HTTPException(status_code=404, detail=f"Strategy {request.strategy_name} not found.")

    try:
        results = run_backtest(
            request.exchange,
            request.symbol,
            request.timeframe,
            request.start_date,
            request.end_date,
            strategy_class
        )
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
