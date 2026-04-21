"""
Memory Manager - User Context & Session Management
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import hashlib

from dotenv import load_dotenv

load_dotenv()


@dataclass
class UserContext:
    user_id: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
    tasks: List[Dict] = field(default_factory=list)
    sessions: Dict[str, Any] = field(default_factory=dict)
    last_active: datetime = field(default_factory=datetime.now)


class MemoryManager:
    def __init__(self):
        self.storage_type = os.getenv("MEMORY_STORAGE", "memory")
        self.contexts: Dict[str, UserContext] = {}
        self.vector_store = None
        self._init_vector_store()

    def _init_vector_store(self):
        try:
            import chromadb
            self.vector_store = chromadb.Client()
        except ImportError:
            pass

    def get_user_context(self, user_id: str) -> UserContext:
        if user_id not in self.contexts:
            self.contexts[user_id] = UserContext(user_id=user_id)
        return self.contexts[user_id]

    def store_interaction(
        self,
        user_id: str,
        user_message: str,
        assistant_response: str,
        metadata: Optional[Dict] = None
    ):
        context = self.get_user_context(user_id)
        interaction = {
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        context.history.append(interaction)
        context.last_active = datetime.now()
        self._store_to_vector(user_id, user_message, assistant_response)

    def get_recent_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        context = self.get_user_context(user_id)
        return context.history[-limit:]

    def get_conversation_context(self, user_id: str) -> List[Dict]:
        context = self.get_user_context(user_id)
        return [
            {"role": "user" if i % 2 == 0 else "assistant", "content": h["user"] if i % 2 == 0 else h["assistant"]}
            for i, h in enumerate(context.history[-10:])
        ]

    def store_preference(self, user_id: str, key: str, value: Any):
        context = self.get_user_context(user_id)
        context.preferences[key] = value

    def get_preference(self, user_id: str, key: str, default: Any = None) -> Any:
        context = self.get_user_context(user_id)
        return context.preferences.get(key, default)

    def add_task(self, user_id: str, task: Dict):
        context = self.get_user_context(user_id)
        task["id"] = hashlib.md5(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        task["created_at"] = datetime.now().isoformat()
        task["status"] = "pending"
        context.tasks.append(task)
        return task

    def get_tasks(self, user_id: str, status: Optional[str] = None) -> List[Dict]:
        context = self.get_user_context(user_id)
        if status:
            return [t for t in context.tasks if t.get("status") == status]
        return context.tasks

    def update_task(self, user_id: str, task_id: str, updates: Dict) -> Optional[Dict]:
        context = self.get_user_context(user_id)
        for task in context.tasks:
            if task.get("id") == task_id:
                task.update(updates)
                return task
        return None

    def store_session(self, user_id: str, session_id: str, data: Dict, ttl: int = 3600):
        context = self.get_user_context(user_id)
        expires = datetime.now() + timedelta(seconds=ttl)
        context.sessions[session_id] = {"data": data, "expires": expires.isoformat()}

    def get_session(self, user_id: str, session_id: str) -> Optional[Dict]:
        context = self.get_user_context(user_id)
        session = context.sessions.get(session_id)
        if session:
            expires = datetime.fromisoformat(session["expires"])
            if datetime.now() < expires:
                return session["data"]
            else:
                del context.sessions[session_id]
        return None

    def _store_to_vector(self, user_id: str, user_message: str, assistant_response: str):
        if not self.vector_store:
            return
        
        try:
            collection = self.vector_store.get_or_create_collection(f"user_{user_id}")
            combined_text = f"User: {user_message}\nAssistant: {assistant_response}"
            collection.add(
                documents=[combined_text],
                ids=[hashlib.md5(combined_text.encode()).hexdigest()[:16]]
            )
        except Exception:
            pass

    def search_memory(self, user_id: str, query: str, limit: int = 5) -> List[Dict]:
        if not self.vector_store:
            return []
        
        try:
            collection = self.vector_store.get_or_create_collection(f"user_{user_id}")
            results = collection.query(query_texts=[query], n_results=limit)
            return results.get("documents", [])
        except Exception:
            return []

    def clear_old_sessions(self):
        now = datetime.now()
        for context in self.contexts.values():
            expired = [
                sid for sid, session in context.sessions.items()
                if datetime.fromisoformat(session["expires"]) < now
            ]
            for sid in expired:
                del context.sessions[sid]