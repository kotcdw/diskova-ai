"""
API Routes - Chat Endpoints
"""

from typing import List, Dict, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends, Request

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    module: str
    metadata: Dict


class ChatHistoryRequest(BaseModel):
    user_id: str
    limit: int = 10


@router.post("/message", response_model=ChatResponse)
async def send_message(
    message: ChatMessage,
    request: Request
):
    router_instance = request.app.state.module_router
    memory_manager = request.app.state.memory_manager
    
    user_id = message.user_id or "anonymous"
    context = message.context or {}
    
    history = memory_manager.get_conversation_context(user_id)
    
    result = router_instance.route(message.message, context, history)
    
    memory_manager.store_interaction(
        user_id=user_id,
        user_message=message.message,
        assistant_response=result.response,
        metadata={"module": result.module}
    )
    
    return ChatResponse(
        response=result.response,
        module=result.module,
        metadata=result.metadata
    )


@router.get("/history/{user_id}")
async def get_history(
    user_id: str,
    request: Request,
    limit: int = 10
):
    memory_manager = request.app.state.memory_manager
    history = memory_manager.get_recent_history(user_id, limit)
    return {"history": history}


@router.post("/clear/{user_id}")
async def clear_history(
    user_id: str,
    request: Request
):
    memory_manager = request.app.state.memory_manager
    context = memory_manager.get_user_context(user_id)
    context.history = []
    return {"status": "cleared"}


@router.post("/task")
async def create_task(
    task: Dict,
    user_id: str,
    request: Request
):
    memory_manager = request.app.state.memory_manager
    new_task = memory_manager.add_task(user_id, task)
    return {"task": new_task}


@router.get("/tasks/{user_id}")
async def get_tasks(
    user_id: str,
    request: Request,
    status: Optional[str] = None
):
    memory_manager = request.app.state.memory_manager
    tasks = memory_manager.get_tasks(user_id, status)
    return {"tasks": tasks}


@router.patch("/task/{user_id}/{task_id}")
async def update_task(
    user_id: str,
    task_id: str,
    updates: Dict,
    request: Request
):
    memory_manager = request.app.state.memory_manager
    task = memory_manager.update_task(user_id, task_id, updates)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task": task}
