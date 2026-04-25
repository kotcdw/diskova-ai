"""
Perception Layer
================
Collects input from various sources: text, voice, images.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional


class VoiceInput:
    """Speech to text for voice input."""
    
    def __init__(self):
        self.available = False
        try:
            import speech_recognition
            self.recognizer = speech_recognition.Recognizer()
            self.available = True
        except ImportError:
            pass
    
    def listen(self, timeout: int = 5) -> Optional[str]:
        """Listen for voice input."""
        if not self.available:
            return None
        
        try:
            with speech_recognition.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio)
                return text
        except:
            return None


class ImageInput:
    """Computer vision for image input."""
    
    def __init__(self):
        self.available = False
    
    def analyze(self, image_path: str) -> Optional[str]:
        """Analyze image and return description."""
        if not Path(image_path).exists():
            return None
        
        try:
            from PIL import Image
            import pytesseract
            
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            self.available = True
            return text.strip()
        except:
            return "Image analysis not available. Install: pip install pytesseract pillow"


class TextInput:
    """Text input processor."""
    
    def __init__(self):
        pass
    
    def process(self, text: str) -> dict:
        """Process text input."""
        if not text or not text.strip():
            return {"valid": False, "text": "", "intent": None}
        
        text = text.strip()
        
        return {
            "valid": True,
            "text": text,
            "length": len(text),
            "has_code": "```" in text or "def " in text or "function" in text,
        }


def get_perception():
    """Get all perception input handlers."""
    return {
        "voice": VoiceInput(),
        "image": ImageInput(),
        "text": TextInput(),
    }


if __name__ == "__main__":
    print("Perception Layer")
    perception = get_perception()
    print(f"Voice: {perception['voice'].available}")
    print("Text: Ready")
    print("Image: Ready")