"""
API Routes - User Management
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


class UserPreferences(BaseModel):
    theme: Optional[str] = "light"
    language: Optional[str] = "en"
    notifications: Optional[bool] = True
    voice_enabled: Optional[bool] = False
    timezone: Optional[str] = "UTC"


@router.get("/{user_id}")
async def get_user(user_id: str, request: Request):
    memory = request.app.state.memory_manager
    context = memory.get_user_context(user_id)
    
    return {
        "id": user_id,
        "preferences": context.preferences,
        "stats": {
            "total_interactions": len(context.history),
            "total_tasks": len(context.tasks),
            "completed_tasks": len([t for t in context.tasks if t.get("status") == "completed"])
        }
    }


@router.put("/{user_id}/preferences")
async def update_preferences(
    user_id: str,
    preferences: UserPreferences,
    request: Request
):
    memory = request.app.state.memory_manager
    
    for key, value in preferences.dict().items():
        if value is not None:
            memory.store_preference(user_id, key, value)
    
    return {"status": "updated", "preferences": preferences.dict()}


@router.get("/{user_id}/stats")
async def get_user_stats(user_id: str, request: Request):
    memory = request.app.state.memory_manager
    context = memory.get_user_context(user_id)
    
    return {
        "total_interactions": len(context.history),
        "total_tasks": len(context.tasks),
        "completed_tasks": len([t for t in context.tasks if t.get("status") == "completed"]),
        "pending_tasks": len([t for t in context.tasks if t.get("status") == "pending"]),
        "last_active": context.last_active.isoformat() if context.last_active else None
    }


@router.delete("/{user_id}")
async def delete_user(user_id: str, request: Request):
    memory = request.app.state.memory_manager
    
    if user_id in memory.contexts:
        del memory.contexts[user_id]
        return {"status": "deleted"}
    
    raise HTTPException(status_code=404, detail="User not found")
