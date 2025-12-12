from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union
from engine.modes.backtest_mode import run_backtest
from engine.strategies.simple_strategy import SimpleStrategy
from engine.controllers.auth_controller import get_current_user
from engine.models.core import User, Task, Log, BacktestSession
from engine.schemas import BacktestResult, TradeResult
import uuid
import time
import json
import os

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

class BacktestSessionResponse(BaseModel):
    id: str
    status: str
    metrics: Optional[Dict] = None
    equity_curve: Optional[List] = None
    trades: Optional[List] = None
    closed_trades: Optional[List] = None
    hyperparameters: Optional[Dict] = None
    chart_data: Optional[Dict] = None
    state: Optional[Dict] = None
    title: Optional[str] = None
    description: Optional[str] = None
    strategy_codes: Optional[Dict] = None
    exception: Optional[str] = None
    traceback: Optional[str] = None
    execution_duration: Optional[float] = None
    created_at: int
    updated_at: int

class BacktestSessionListResponse(BaseModel):
    sessions: List[BacktestSessionResponse]
    count: int

class StrategiesResponse(BaseModel):
    strategies: List[str]

class PaginationRequest(BaseModel):
    page: int = 1
    limit: int = 10
    offset: int = 0

class UpdateSessionStateRequest(BaseModel):
    id: str
    state: Dict

class UpdateSessionNotesRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    strategy_codes: Optional[Dict] = None

class MessageResponse(BaseModel):
    message: str

class LogsResponse(BaseModel):
    content: str

class PurgeResponse(BaseModel):
    message: str
    deleted_count: int

class ChartDataResponse(BaseModel):
    chart_data: Optional[Dict] = None

class StrategyCodeResponse(BaseModel):
    strategy_code: Optional[Dict] = None

STRATEGIES = {
    "SimpleStrategy": SimpleStrategy
}

@router.get("/strategies", response_model=StrategiesResponse)
def get_strategies():
    """
    Get list of available strategies.
    """
    return {"strategies": list(STRATEGIES.keys())}

@router.post("/cancel", response_model=MessageResponse)
def cancel_backtest(request: Dict[str, str], current_user: User = Depends(get_current_user)):
    """
    Cancel a running backtest process.
    """
    session_id = request.get('id')
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")
        
    try:
        session = BacktestSession.get(BacktestSession.id == session_id)
        if session.status in ['processing', 'queued']:
            session.status = 'cancelled'
            session.save()
            return {"message": f"Backtest {session_id} requested for cancellation"}
        else:
            return {"message": f"Backtest {session_id} is already {session.status}"}
    except BacktestSession.DoesNotExist:
        raise HTTPException(status_code=404, detail="Session not found")

@router.get("/logs/{session_id}", response_model=LogsResponse)
def get_logs(session_id: str, current_user: User = Depends(get_current_user)):
    """
    Get logs for a specific session.
    """
    logs = Log.select().where(Log.session_id == session_id).order_by(Log.timestamp)
    log_content = "\n".join([f"[{l.type}] {l.message}" for l in logs])
    return {"content": log_content}

@router.post("/purge-sessions", response_model=PurgeResponse)
def purge_sessions(request: Dict[str, int], current_user: User = Depends(get_current_user)):
    """
    Purge backtest sessions older than specified days.
    """
    days_old = request.get('days_old')
    if not days_old:
        raise HTTPException(status_code=400, detail="days_old is required")
        
    cutoff_time = int(time.time() * 1000) - (days_old * 86400 * 1000) # ms
    query = BacktestSession.delete().where(BacktestSession.created_at < cutoff_time)
    deleted_count = query.execute()
    
    return {"message": f"Successfully purged {deleted_count} session(s)", "deleted_count": deleted_count}

@router.get("/sessions/{session_id}/chart-data", response_model=ChartDataResponse)
def get_backtest_session_chart_data(session_id: str, current_user: User = Depends(get_current_user)):
    """
    Get chart data for a specific backtest session.
    """
    try:
        session = BacktestSession.get(BacktestSession.id == session_id)
    except BacktestSession.DoesNotExist:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return {"chart_data": session.chart_data_json}

@router.post("/sessions", response_model=BacktestSessionListResponse)
def get_backtest_sessions(pagination: PaginationRequest, current_user: User = Depends(get_current_user)):
    """
    Get a list of backtest sessions sorted by most recently updated.
    """
    query = BacktestSession.select().order_by(BacktestSession.updated_at.desc())
    count = query.count()
    sessions = query.limit(pagination.limit).offset(pagination.offset)
    
    session_list = []
    for s in sessions:
        session_list.append(BacktestSessionResponse(
            id=s.id,
            status=s.status,
            metrics=s.metrics_json,
            equity_curve=s.equity_curve_json,
            trades=s.trades_json,
            closed_trades=s.closed_trades_json,
            hyperparameters=s.hyperparameters_json,
            chart_data=s.chart_data_json,
            state=s.state_json,
            title=s.title,
            description=s.description,
            strategy_codes=s.strategy_codes_json,
            exception=s.exception,
            traceback=s.traceback,
            execution_duration=s.execution_duration,
            created_at=s.created_at,
            updated_at=s.updated_at
        ))
        
    return {"sessions": session_list, "count": count}

@router.get("/sessions/{session_id}/logs")
def get_backtest_logs(session_id: str):
    path = f"storage/logs/backtest-mode/{session_id}.txt"
    
    if not os.path.exists(path):
        return PlainTextResponse("")
        
    with open(path, "r") as f:
        content = f.read()
        
    return PlainTextResponse(content)

@router.get("/sessions/{session_id}", response_model=BacktestSessionResponse)
def get_backtest_session(session_id: str, current_user: User = Depends(get_current_user)):
    """
    Get a single backtest session by ID.
    """
    try:
        s = BacktestSession.get(BacktestSession.id == session_id)
    except BacktestSession.DoesNotExist:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return BacktestSessionResponse(
        id=s.id,
        status=s.status,
        metrics=s.metrics_json,
        equity_curve=s.equity_curve_json,
        trades=s.trades_json,
        closed_trades=s.closed_trades_json,
        hyperparameters=s.hyperparameters_json,
        chart_data=s.chart_data_json,
        state=s.state_json,
        title=s.title,
        description=s.description,
        strategy_codes=s.strategy_codes_json,
        exception=s.exception,
        traceback=s.traceback,
        execution_duration=s.execution_duration,
        created_at=s.created_at,
        updated_at=s.updated_at
    )

@router.delete("/sessions/{session_id}", response_model=MessageResponse)
def remove_backtest_session(session_id: str, current_user: User = Depends(get_current_user)):
    """
    Remove a backtest session from the database.
    """
    query = BacktestSession.delete().where(BacktestSession.id == session_id)
    deleted_count = query.execute()
    
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return {"message": "Session removed successfully"}

@router.post("/update-state", response_model=MessageResponse)
def update_session_state(request: UpdateSessionStateRequest, current_user: User = Depends(get_current_user)):
    """
    Update the state of a backtest session.
    """
    try:
        session = BacktestSession.get(BacktestSession.id == request.id)
        session.state = json.dumps(request.state)
        session.updated_at = int(time.time() * 1000)
        session.save()
        return {"message": "Backtest session state updated successfully"}
    except BacktestSession.DoesNotExist:
        raise HTTPException(status_code=404, detail="Session not found")

@router.post("/sessions/{session_id}/notes", response_model=MessageResponse)
def update_session_notes(session_id: str, request: UpdateSessionNotesRequest, current_user: User = Depends(get_current_user)):
    """
    Update the notes (title, description, strategy_codes) of a backtest session.
    """
    try:
        session = BacktestSession.get(BacktestSession.id == session_id)
        if request.title is not None:
            session.title = request.title
        if request.description is not None:
            session.description = request.description
        if request.strategy_codes is not None:
            session.strategy_codes = json.dumps(request.strategy_codes)
        
        session.updated_at = int(time.time() * 1000)
        session.save()
        return {"message": "Backtest session notes updated successfully"}
    except BacktestSession.DoesNotExist:
        raise HTTPException(status_code=404, detail="Session not found")

@router.post("/sessions/{session_id}/strategy-code", response_model=StrategyCodeResponse)
def get_backtest_session_strategy_codes(session_id: str, current_user: User = Depends(get_current_user)):
    """
    Get strategy codes for a specific backtest session.
    """
    try:
        session = BacktestSession.get(BacktestSession.id == session_id)
        return {"strategy_code": session.strategy_codes_json}
    except BacktestSession.DoesNotExist:
        raise HTTPException(status_code=404, detail="Session not found")


def backtest_task(task_id: str, request: BacktestRequest, strategy_class):
    try:
        # Update session to processing
        session = BacktestSession.get(BacktestSession.id == task_id)
        session.status = "processing"
        session.updated_at = int(time.time() * 1000)
        session.save()
        
        results = run_backtest(
            request.exchange,
            request.symbol,
            request.timeframe,
            request.start_date,
            request.end_date,
            strategy_class,
            task_id=task_id
        )
        
        # Update BacktestSession with results
        session = BacktestSession.get(BacktestSession.id == task_id)
        session.status = "completed"
        session.metrics = json.dumps({
            "initial_balance": results.initial_balance,
            "final_balance": results.final_balance,
            "pnl_percent": results.pnl_percent
        })
        session.trades = json.dumps([t.model_dump() for t in results.trades])
        session.closed_trades = json.dumps([t.model_dump() for t in results.closed_trades])
        session.updated_at = int(time.time() * 1000)
        session.save()
        
    except Exception as e:
        print(f"Backtest failed: {e}")
        # Update status to failed
        try:
            session = BacktestSession.get(BacktestSession.id == task_id)
            session.status = "failed"
            session.exception = str(e)
            session.updated_at = int(time.time() * 1000)
            session.save()
        except:
            pass

@router.post("/backtest", response_model=BacktestResponse)
async def trigger_backtest(request: BacktestRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """
    Run a backtest. Always runs in background.
    """
    strategy_class = STRATEGIES.get(request.strategy_name)
    if not strategy_class:
        raise HTTPException(status_code=404, detail=f"Strategy {request.strategy_name} not found.")

    task_id = str(uuid.uuid4())
    
    # Create BacktestSession immediately with queued status
    try:
        BacktestSession.create(
            id=task_id,
            status="queued",
            created_at=int(time.time() * 1000),
            updated_at=int(time.time() * 1000)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

    background_tasks.add_task(backtest_task, task_id, request, strategy_class)
    
    return {
        "message": "Backtest started in background", 
        "status": "queued",
        "task_id": task_id
    }
