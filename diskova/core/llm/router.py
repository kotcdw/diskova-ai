"""
AI Core - Module Router
Routes requests to appropriate LLM provider and modules
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

import openai
from dotenv import load_dotenv

load_dotenv()


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    MISTRAL = "mistral"


@dataclass
class ModuleResult:
    module: str
    response: str
    metadata: Dict[str, Any]


class ModuleRouter:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai")
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        self.modules = {
            "secretary": self._route_secretary,
            "finance": self._route_finance,
            "security": self._route_security,
            "knowledge": self._route_knowledge,
            "voice": self._route_voice,
            "automation": self._route_automation,
            "communication": self._route_communication,
            "documents": self._route_documents,
            "auditor": self._route_auditor,
        }
        
        self._setup_client()

    def _setup_client(self):
        if self.provider == "openai" and self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def route(self, user_input: str, context: Dict[str, Any], history: List[Dict]) -> ModuleResult:
        detected_module = self._detect_module(user_input, context)
        handler = self.modules.get(detected_module, self._route_default)
        return handler(user_input, context, history)

    def _detect_module(self, user_input: str, context: Dict) -> str:
        intent_keywords = {
            "secretary": ["schedule", "meeting", "remind", "task", "todo", "calendar", "book", "organize"],
            "finance": ["budget", "expense", "money", "cost", "spending", "income", "payment", "invoice"],
            "security": ["login", "password", "security", "alert", "access", "permission", "verify"],
            "knowledge": ["news", "research", "find", "search", "information", "update", "trend"],
            "voice": ["speak", "voice", "audio", "listen", "hear", "call", "speech"],
            "automation": ["auto", "workflow", "trigger", "schedule", "automatic", "routine"],
            "communication": ["email", "message", "send", "compose", "reply", "contact"],
            "documents": ["document", "pdf", "file", "report", "summary", "read", "write"],
            "auditor": ["audit", "compliance", "check", "verify", "review", "analyze"],
        }
        
        user_lower = user_input.lower()
        for module, keywords in intent_keywords.items():
            if any(kw in user_lower for kw in keywords):
                return module
        return "general"

    def _route_secretary(self, user_input: str, context: Dict, history: List[Dict]) -> ModuleResult:
        return self._call_llm(user_input, context, history)

    def _route_finance(self, user_input: str, context: Dict, history: List[Dict]) -> ModuleResult:
        return self._call_llm(user_input, context, history)

    def _route_security(self, user_input: str, context: Dict, history: List[Dict]) -> ModuleResult:
        return self._call_llm(user_input, context, history)

    def _route_knowledge(self, user_input: str, context: Dict, history: List[Dict]) -> ModuleResult:
        return self._call_llm(user_input, context, history)

    def _route_voice(self, user_input: str, context: Dict, history: List[Dict]) -> ModuleResult:
        return self._call_llm(user_input, context, history)

    def _route_automation(self, user_input: str, context: Dict, history: List[Dict]) -> ModuleResult:
        return self._call_llm(user_input, context, history)

    def _route_communication(self, user_input: str, context: Dict, history: List[Dict]) -> ModuleResult:
        return self._call_llm(user_input, context, history)

    def _route_documents(self, user_input: str, context: Dict, history: List[Dict]) -> ModuleResult:
        return self._call_llm(user_input, context, history)

    def _route_auditor(self, user_input: str, context: Dict, history: List[Dict]) -> ModuleResult:
        return self._call_llm(user_input, context, history)

    def _route_default(self, user_input: str, context: Dict, history: List[Dict]) -> ModuleResult:
        return self._call_llm(user_input, context, history)

    def _call_llm(self, user_input: str, context: Dict, history: List[Dict]) -> ModuleResult:
        if not self.client:
            return ModuleResult(
                module="general",
                response="I'm here to help! Please configure your LLM provider to enable AI responses.",
                metadata={}
            )

        messages = self._build_messages(user_input, context, history)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            return ModuleResult(
                module="general",
                response=response.choices[0].message.content,
                metadata={"model": self.model, "usage": dict(response.usage)}
            )
        except Exception as e:
            return ModuleResult(
                module="general",
                response=f"I encountered an error: {str(e)}",
                metadata={"error": True}
            )

    def _build_messages(self, user_input: str, context: Dict, history: List[Dict]) -> List[Dict]:
        system_prompt = """You are Diskova+, an intelligent African AI assistant. 
You help with tasks, scheduling, finance, knowledge, and more.
Be helpful, concise, and culturally aware.
Always prioritize user security and privacy."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            *[{"role": h["role"], "content": h["content"]} for h in history[-5:]],
            {"role": "user", "content": user_input}
        ]
        return messages

    def call_ollama(self, prompt: str, model: str = "mistral") -> str:
        if not self.client:
            return "Ollama not configured"
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"