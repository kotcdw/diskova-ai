import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

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
        self.client = None

    def _load_config(self) -> DBConfig:
        db_type = os.getenv("DB_TYPE", "memory")
        if db_type == "firebase":
            return DBConfig(
                type="firebase",
                project_id=os.getenv("FIREBASE_PROJECT_ID", ""),
                api_key=os.getenv("FIREBASE_API_KEY")
            )
        else:
            return DBConfig(
                type="memory",
                project_id="",
                url=None
            )

    def store(self, collection: str, data: Dict, doc_id: Optional[str] = None) -> str:
        return f"stored-{collection}"

    def get(self, collection: str, doc_id: str) -> Optional[Dict]:
        return None

    def query(self, collection: str, filters: List[Dict], limit: int = 100) -> List[Dict]:
        return []

    def delete(self, collection: str, doc_id: str) -> bool:
        return True