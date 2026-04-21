"""
API Routes - Voice Endpoints (STT/TTS)
"""

import base64
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


class SpeechRequest(BaseModel):
    audio: str  # Base64 encoded audio
    language: Optional[str] = "en"


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "alloy"
    speed: Optional[float] = 1.0


@router.post("/speech-to-text")
async def speech_to_text(req: SpeechRequest, request: Request):
    voice_module = request.app.state.voice_module
    
    audio_data = base64.b64decode(req.audio)
    text = voice_module.speech_to_text(audio_data, req.language)
    
    return {"text": text, "language": req.language}


@router.post("/text-to-speech")
async def text_to_speech(req: TTSRequest, request: Request):
    voice_module = request.app.state.voice_module
    
    audio_data = voice_module.text_to_speech(req.text, req.voice, req.speed)
    
    if not audio_data:
        raise HTTPException(status_code=500, detail="Failed to generate audio")
    
    audio_url = f"data:audio/mp3;base64,{base64.b64encode(audio_data).decode()}"
    
    return {"audio_url": audio_url, "voice": req.voice}


@router.get("/voices")
async def get_voices(request: Request):
    voice_module = request.app.state.voice_module
    voices = voice_module.get_available_voices()
    return {"voices": voices}


@router.get("/status")
async def voice_status(request: Request):
    return {
        "voice_enabled": True,
        "stt_provider": "openai_whisper",
        "tts_provider": "openai_tts"
    }