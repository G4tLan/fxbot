from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union
from engine.modes.backtest_mode import run_backtest
from engine.strategies.simple_strategy import SimpleStrategy
from engine.controllers.auth_controller import get_current_user
from engine.models.core import User, Task
from engine.schemas import BacktestResult, TradeResult
import uuid
import time
import json

router = APIRouter()

class BacktestRequest(BaseModel):
    exchange: str
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    strategy_name: str
    run_in_background: Optional[bool] = False

class BacktestResponse(BaseModel):
    status: str
    message: str
    results: Optional[BacktestResult] = None
    task_id: Optional[str] = None

class StrategiesResponse(BaseModel):
    strategies: List[str]

STRATEGIES = {
    "SimpleStrategy": SimpleStrategy
}

@router.get("/strategies", response_model=StrategiesResponse)
def get_strategies():
    """
    Get list of available strategies.
    """
    return {"strategies": list(STRATEGIES.keys())}

def backtest_task(task_id: str, request: BacktestRequest, strategy_class):
    try:
        # Update status to processing
        Task.update(status="processing", updated_at=int(time.time())).where(Task.id == task_id).execute()
        
        results = run_backtest(
            request.exchange,
            request.symbol,
            request.timeframe,
            request.start_date,
            request.end_date,
            strategy_class
        )
        
        # Update status to completed
        Task.update(
            status="completed", 
            result=results.json(),
            updated_at=int(time.time())
        ).where(Task.id == task_id).execute()
        
    except Exception as e:
        print(f"Backtest failed: {e}")
        # Update status to failed
        Task.update(
            status="failed", 
            error=str(e),
            updated_at=int(time.time())
        ).where(Task.id == task_id).execute()

@router.post("/backtest", response_model=BacktestResponse)
async def trigger_backtest(request: BacktestRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """
    Run a backtest. Can be synchronous or asynchronous based on run_in_background flag.
    """
    strategy_class = STRATEGIES.get(request.strategy_name)
    if not strategy_class:
        raise HTTPException(status_code=404, detail=f"Strategy {request.strategy_name} not found.")

    if request.run_in_background:
        task_id = str(uuid.uuid4())
        
        # Create Task record
        Task.create(
            id=task_id,
            type="backtest",
            status="queued",
            created_at=int(time.time()),
            updated_at=int(time.time())
        )
        
        background_tasks.add_task(backtest_task, task_id, request, strategy_class)
        
        return {
            "message": "Backtest started in background", 
            "status": "queued",
            "task_id": task_id
        }
    else:
        # Synchronous execution
        task_id = str(uuid.uuid4())
        
        # Create Task record
        Task.create(
            id=task_id,
            type="backtest",
            status="processing",
            created_at=int(time.time()),
            updated_at=int(time.time())
        )
        
        try:
            results = run_backtest(
                request.exchange,
                request.symbol,
                request.timeframe,
                request.start_date,
                request.end_date,
                strategy_class
            )
            
            # Update Task
            Task.update(
                status="completed", 
                result=results.json(),
                updated_at=int(time.time())
            ).where(Task.id == task_id).execute()
            
            return {
                "status": "completed", 
                "message": "Backtest completed successfully", 
                "results": results,
                "task_id": task_id
            }
        except Exception as e:
            Task.update(
                status="failed", 
                error=str(e),
                updated_at=int(time.time())
            ).where(Task.id == task_id).execute()
            raise HTTPException(status_code=500, detail=str(e))
