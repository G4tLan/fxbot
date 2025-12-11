from fastapi import APIRouter, HTTPException, Depends
from engine.models.core import Task, User
from engine.controllers.auth_controller import get_current_user
from playhouse.shortcuts import model_to_dict
from pydantic import BaseModel
from typing import Optional, Any, List, Dict, Union
import json

router = APIRouter()

class TaskResponse(BaseModel):
    id: str
    type: str
    status: str
    result: Optional[Union[Dict[str, Any], List[Any], str]] = None
    error: Optional[str] = None
    created_at: int
    updated_at: int

@router.get("/tasks/{task_id}", response_model=TaskResponse)
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

@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(limit: int = 20, offset: int = 0, current_user: User = Depends(get_current_user)):
    tasks = Task.select().order_by(Task.created_at.desc()).limit(limit).offset(offset)
    result_list = []
    for t in tasks:
        t_dict = model_to_dict(t)
        if t_dict.get('result') and isinstance(t_dict['result'], str):
            try:
                t_dict['result'] = json.loads(t_dict['result'])
            except:
                pass
        result_list.append(t_dict)
    return result_list
