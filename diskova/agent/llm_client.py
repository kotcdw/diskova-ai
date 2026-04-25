"""
LM Studio Integration
====================
Local LLM inference via LM Studio local API.

LM Studio: https://lmstudio.ai
- Download models in GGUF format (faster than Ollama)
- Local inference server on port 1234
- OpenAI-compatible API
"""

import os
import json
import requests
from typing import Optional, Dict, List, Any


class LMStudioClient:
    """
    Client for LM Studio local inference.
    
    Usage:
        client = LMStudioClient()
        response = client.chat("Write hello world in Python")
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        model: str = None
    ):
        self.base_url = base_url
        self.model = model
        self._session = requests.Session()
    
    def is_running(self) -> bool:
        """Check if LM Studio is running."""
        try:
            response = self._session.get(
                f"{self.base_url}/models",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[Dict]:
        """List available models."""
        try:
            response = self._session.get(
                f"{self.base_url}/models",
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get("data", [])
        except:
            pass
        return []
    
    def chat(
        self,
        message: str,
        system_prompt: str = "You are a helpful coding assistant.",
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Send a chat message and get response.
        
        Args:
            message: User message
            system_prompt: System prompt
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
        
        Returns:
            AI response text
        """
        if not self.is_running():
            return "LM Studio not running. Start LM Studio and load a model."
        
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "model": self.model
        }
        
        try:
            response = self._session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=120
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            return f"Error: {e}"
        
        return "(no response)"
    
    def complete(
        self,
        prompt: str,
        max_tokens: int = 256
    ) -> str:
        """Get completion for a prompt."""
        if not self.is_running():
            return "LM Studio not running."
        
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "model": self.model
        }
        
        try:
            response = self._session.post(
                f"{self.base_url}/completions",
                json=payload,
                timeout=120
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("text", "")
        except Exception as e:
            return f"Error: {e}"
        
        return "(no response)"


class OllamaClient:
    """
    Client for Ollama (alternative to LM Studio).
    
    Works with Ollama: https://ollama.com
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen2.5-coder:1.5b"
    ):
        self.base_url = base_url
        self.model = model
    
    def is_running(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[Dict]:
        """List available models."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get("models", [])
        except:
            pass
        return []
    
    def chat(
        self,
        message: str,
        system_prompt: str = "You are a helpful coding assistant.",
        temperature: float = 0.7
    ) -> str:
        """Send chat message."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")
        except Exception as e:
            return f"Error: {e}"
        
        return "(no response)"
    
    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7
    ) -> str:
        """Generate completion."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
        except Exception as e:
            return f"Error: {e}"
        
        return "(no response)"


def get_llm_client(
    provider: str = "auto"
) -> Any:
    """
    Get LLM client.
    
    Args:
        provider: "ollama", "lmstudio", or "auto" (tries both)
    
    Returns:
        Client instance
    """
    if provider == "auto":
        ollama = OllamaClient()
        if ollama.is_running():
            return ollama
        lmstudio = LMStudioClient()
        if lmstudio.is_running():
            return lmstudio
        return None
    
    if provider == "ollama":
        return OllamaClient()
    if provider == "lmstudio":
        return LMStudioClient()
    
    return None


if __name__ == "__main__":
    print("=" * 50)
    print("🤖 LLM Client Test")
    print("=" * 50)
    
    # Test Ollama
    print("\n📡 Testing Ollama...")
    ollama = OllamaClient()
    if ollama.is_running():
        print("✅ Ollama is running!")
        models = ollama.list_models()
        print(f"   Models: {[m.get('name') for m in models]}")
        
        print("\n💬 Testing chat...")
        response = ollama.chat("Hi! Write 'hello' in Python.")
        print(f"   Response: {response[:100]}...")
    else:
        print("❌ Ollama not running")
    
    # Test LM Studio
    print("\n📡 Testing LM Studio...")
    lmstudio = LMStudioClient()
    if lmstudio.is_running():
        print("✅ LM Studio is running!")
        print("   Note: Load a model in LM Studio first")
    else:
        print("❌ LM Studio not running")
        print("   Download from: https://lmstudio.ai")
    
    print("\n" + "=" * 50)