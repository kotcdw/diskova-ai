"""
API Routes - Module Endpoints
"""

from typing import Optional, Dict, List
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/list")
async def list_modules(request: Request):
    return {
        "modules": [
            {
                "id": "secretary",
                "name": "Secretary & Admin",
                "description": "Scheduling, tasks, reminders",
                "status": "active"
            },
            {
                "id": "finance",
                "name": "Finance Advisor",
                "description": "Budget tracking, forecasting",
                "status": "active"
            },
            {
                "id": "security",
                "name": "Security Guardian",
                "description": "Auth, monitoring, alerts",
                "status": "active"
            },
            {
                "id": "knowledge",
                "name": "Knowledge Engine",
                "description": "News, research, trends",
                "status": "active"
            },
            {
                "id": "voice",
                "name": "Voice Interface",
                "description": "Speech input/output",
                "status": "coming_soon"
            },
            {
                "id": "automation",
                "name": "Automation Engine",
                "description": "Workflows, triggers",
                "status": "active"
            },
            {
                "id": "communication",
                "name": "Communication Hub",
                "description": "Email, messages, contacts",
                "status": "active"
            },
            {
                "id": "documents",
                "name": "Document Intelligence",
                "description": "PDF, reports, summaries",
                "status": "active"
            },
            {
                "id": "auditor",
                "name": "Compliance Auditor",
                "description": "Checks, audits, compliance",
                "status": "coming_soon"
            }
        ]
    }


@router.get("/{module_id}/status")
async def get_module_status(module_id: str, request: Request):
    available_modules = [
        "secretary", "finance", "security", "knowledge",
        "voice", "automation", "communication", "documents", "auditor"
    ]
    
    if module_id not in available_modules:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return {
        "module": module_id,
        "status": "active" if module_id != "voice" and module_id != "auditor" else "coming_soon",
        "version": "1.0.0"
    }


class ModuleConfig(BaseModel):
    settings: Dict


@router.put("/{module_id}/config")
async def update_module_config(
    module_id: str,
    config: ModuleConfig,
    user_id: str,
    request: Request
):
    memory = request.app.state.memory_manager
    memory.store_preference(f"module_{module_id}_config", user_id, config.settings)
    
    return {"status": "updated", "module": module_id}


@router.get("/{module_id}/config/{user_id}")
async def get_module_config(module_id: str, user_id: str, request: Request):
    memory = request.app.state.memory_manager
    config = memory.get_preference(f"module_{module_id}_config", user_id, {})
    
    return {"module": module_id, "config": config}
