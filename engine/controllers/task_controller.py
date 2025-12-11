from fastapi import APIRouter, HTTPException, Depends
from engine.models.core import Task, User
from engine.controllers.auth_controller import get_current_user
from playhouse.shortcuts import model_to_dict
import json

router = APIRouter()

@router.get("/tasks/{task_id}")
async def get_task(task_id: str, current_user: User = Depends(get_current_user)):
    task = Task.get_or_none(Task.id == task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_dict = model_to_dict(task)
    # Parse JSON fields if they are strings
    if task_dict.get('result') and isinstance(task_dict['result'], str):
        try:
            task_dict['result'] = json.loads(task_dict['result'])
        except:
            pass
            
    return task_dict

@router.get("/tasks")
async def list_tasks(limit: int = 20, offset: int = 0, current_user: User = Depends(get_current_user)):
    tasks = Task.select().order_by(Task.created_at.desc()).limit(limit).offset(offset)
    return [model_to_dict(t) for t in tasks]
