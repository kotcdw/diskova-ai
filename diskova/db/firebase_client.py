"""
Database Client - Simple in-memory storage for MVP
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class DBConfig:
    type: str
    project_id: str
    api_key: Optional[str] = None
    url: Optional[str] = None


class FirebaseClient:
    def __init__(self, config: Optional[DBConfig] = None):
        self.config = config or self._load_config()
        self._storage: Dict[str, Dict] = {}

    def _load_config(self) -> DBConfig:
        db_type = os.getenv("DB_TYPE", "memory")
        return DBConfig(
            type=db_type,
            project_id=os.getenv("FIREBASE_PROJECT_ID", ""),
            api_key=os.getenv("FIREBASE_API_KEY")
        )

    def store(self, collection: str, data: Dict, doc_id: Optional[str] = None) -> str:
        key = f"{collection}:{doc_id or 'default'}"
        self._storage[key] = data
        return key

    def get(self, collection: str, doc_id: str) -> Optional[Dict]:
        key = f"{collection}:{doc_id}"
        return self._storage.get(key)

    def query(self, collection: str, filters: List[Dict], limit: int = 100) -> List[Dict]:
        return [v for k, v in self._storage.items() if k.startswith(collection)]

    def delete(self, collection: str, doc_id: str) -> bool:
        key = f"{collection}:{doc_id}"
        if key in self._storage:
            del self._storage[key]
            return True
        return False