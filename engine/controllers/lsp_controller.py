from fastapi import APIRouter, Depends
from pydantic import BaseModel
from engine.controllers.auth_controller import get_current_user
from engine.models.core import User

router = APIRouter()

class LspConfigResponse(BaseModel):
    ws_port: int
    ws_path: str
    enabled: bool

@router.get("/lsp-config", response_model=LspConfigResponse)
async def get_lsp_config(current_user: User = Depends(get_current_user)):
    # In a real implementation, these might come from config.py or env vars
    # For now, we return default values for a local python-lsp-server
    return LspConfigResponse(
        ws_port=3000,  # Default port for many LSP proxies
        ws_path="/python",
        enabled=True
    )
