from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from engine.config import config

router = APIRouter()

class ConfigRequestJson(BaseModel):
    updates: Dict[str, Any]

@router.post("/config/get")
async def get_config():
    return config

@router.post("/config/update")
async def update_config(request: ConfigRequestJson):
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
