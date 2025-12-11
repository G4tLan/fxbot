from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
from engine.config import config
from engine.controllers.auth_controller import get_current_user
from engine.models.core import User

router = APIRouter()

class ConfigRequestJson(BaseModel):
    updates: Dict[str, Any]

@router.post("/config/get")
async def get_config(current_user: User = Depends(get_current_user)):
    return config

@router.post("/config/update")
async def update_config(request: ConfigRequestJson, current_user: User = Depends(get_current_user)):
    try:
        # Deep update or simple top-level update?
        # For simplicity, we'll do a top-level update for now
        # In a real app, we'd want a recursive update function
        for key, value in request.updates.items():
            if key in config:
                if isinstance(config[key], dict) and isinstance(value, dict):
                    config[key].update(value)
                else:
                    config[key] = value
            else:
                # Allow adding new keys? Or strict schema?
                # Allowing new keys for flexibility
                config[key] = value
        
        return {"status": "success", "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
