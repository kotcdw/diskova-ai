"""
Voice Module - Speech-to-Text & Text-to-Speech
"""

import os
import base64
import tempfile
from typing import Optional, Dict
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class VoiceConfig:
    stt_provider: str = "openai"
    tts_provider: str = "openai"
    language: str = "en-US"


class VoiceModule:
    def __init__(self, memory_manager, config: Optional[VoiceConfig] = None):
        self.memory = memory_manager
        self.config = config or VoiceConfig()

    def speech_to_text(self, audio_data: bytes, language: str = "en") -> str:
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return "OpenAI API key required for voice"

            client = openai.OpenAI(api_key=api_key)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as f:
                f.write(audio_data)
                f.flush()
                with open(f.name, "rb") as audio_file:
                    response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language
                    )
            
            return response.text

        except Exception as e:
            return f"Speech recognition error: {str(e)}"

    def text_to_speech(
        self,
        text: str,
        voice: str = "alloy",
        speed: float = 1.0
    ) -> bytes:
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return b""

            client = openai.OpenAI(api_key=api_key)
            
            response = client.audio.speech.create(
                model="tts-1",
                input=text,
                voice=voice,
                speed=speed
            )
            
            return response.content

        except Exception as e:
            return b""

    def transcribe_file(self, file_path: str, language: str = "en") -> str:
        try:
            with open(file_path, "rb") as f:
                audio_data = f.read()
            return self.speech_to_text(audio_data, language)
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_audio_url(self, text: str, voice: str = "alloy") -> str:
        audio_data = self.text_to_speech(text, voice)
        if audio_data:
            return f"data:audio/mp3;base64,{base64.b64encode(audio_data).decode()}"
        return ""

    def get_available_voices(self) -> Dict:
        return {
            "openai": [" alloy", "echo", "fable", "onyx", "nova", "shimmer"],
            "microsoft": ["en-US-GuyNeural", "en-US-JennyNeural"]
        }

    def detect_language(self, audio_data: bytes) -> str:
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return "en"

            client = openai.OpenAI(api_key=api_key)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as f:
                f.write(audio_data)
                f.flush()
                with open(f.name, "rb") as audio_file:
                    response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
            
            return "detected"

        except Exception:
            return "en"