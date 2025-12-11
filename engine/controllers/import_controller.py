from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from engine.modes.import_candles_mode import run_import
from engine.controllers.auth_controller import get_current_user
from engine.models.core import User

router = APIRouter()

class ImportRequest(BaseModel):
    exchange: str
    symbol: str
    start_date: str

def import_task(exchange: str, symbol: str, start_date: str):
    try:
        run_import(exchange, symbol, start_date)
    except Exception as e:
        print(f"Import failed: {e}")

@router.post("/import")
async def trigger_import(request: ImportRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """
    Trigger a background task to import candles.
    """
    background_tasks.add_task(import_task, request.exchange, request.symbol, request.start_date)
    return {"message": f"Import started for {request.symbol} from {request.exchange}", "status": "queued"}
