"""
DISKOVA+ - Lightweight Enterprise AI Brain Assistant
Main Application Entry Point
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from diskova.api import router as chat_router
import diskova.api.auth as auth
import diskova.api.users as users
import diskova.api.modules as modules
import diskova.api.voice as voice_api
from diskova.core.llm.router import ModuleRouter
from diskova.core.memory.manager import MemoryManager
from diskova.db.firebase_client import FirebaseClient
from diskova.modules.voice import VoiceModule

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.module_router = ModuleRouter()
    app.state.memory_manager = MemoryManager()
    app.state.firebase = FirebaseClient()
    app.state.voice_module = VoiceModule(app.state.memory_manager)
    yield
    pass


app = FastAPI(
    title="DISKOVA+ API",
    description="African AI Operating System for Work & Life",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.get("/")
async def root():
    return {
        "name": "DISKOVA+",
        "version": "1.0.0",
        "tagline": "African AI Operating System",
        "status": "running",
        "modules": [
            "secretary", "finance", "security", "knowledge",
            "voice", "automation", "communication", "documents", "auditor"
        ]
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_core": "ready",
        "memory": "connected",
        "database": "connected"
    }


app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(modules.router, prefix="/api/modules", tags=["Modules"])
app.include_router(voice_api.router, prefix="/api/voice", tags=["Voice"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)