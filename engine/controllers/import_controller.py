from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from engine.modes.import_candles_mode import run_import
from engine.controllers.auth_controller import get_current_user
from engine.models.core import User, Task
import uuid
import time
import json

router = APIRouter()

class ImportRequest(BaseModel):
    exchange: str
    symbol: str
    start_date: str

def import_task(task_id: str, exchange: str, symbol: str, start_date: str):
    try:
        # Update status to processing
        Task.update(status="processing", updated_at=int(time.time())).where(Task.id == task_id).execute()
        
        run_import(exchange, symbol, start_date)
        
        # Update status to completed
        Task.update(
            status="completed", 
            result=json.dumps({"message": "Import successful"}),
            updated_at=int(time.time())
        ).where(Task.id == task_id).execute()
        
    except Exception as e:
        print(f"Import failed: {e}")
        # Update status to failed
        Task.update(
            status="failed", 
            error=str(e),
            updated_at=int(time.time())
        ).where(Task.id == task_id).execute()

@router.post("/import")
async def trigger_import(request: ImportRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """
    Trigger a background task to import candles.
    """
    task_id = str(uuid.uuid4())
    
    # Create Task record
    Task.create(
        id=task_id,
        type="import",
        status="queued",
        created_at=int(time.time()),
        updated_at=int(time.time())
    )
    
    background_tasks.add_task(import_task, task_id, request.exchange, request.symbol, request.start_date)
    
    return {
        "message": f"Import started for {request.symbol} from {request.exchange}", 
        "status": "queued",
        "task_id": task_id
    }
