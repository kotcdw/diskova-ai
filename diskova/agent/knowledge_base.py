"""
Knowledge Base (RAG)
====================
More robust long-term memory using ChromaDB.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any


class KnowledgeBase:
    """Knowledge base with RAG for document storage and retrieval."""
    
    def __init__(self, persist_dir: str = None):
        self.persist_dir = Path(persist_dir or "./data/knowledge")
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = "diskova_knowledge"
        self.collection = None
        self._init_chroma()
    
    def _init_chroma(self):
        """Initialize ChromaDB client."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            self.client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(anonymized_telemetry=False)
            )
            
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Diskova AI Knowledge Base"}
                )
        except ImportError:
            print("ChromaDB not installed. Run: pip install chromadb")
            self.client = None
    
    def add_document(
        self,
        content: str,
        metadata: Dict[str, Any] = None,
        doc_id: str = None
    ):
        """Add a document to knowledge base."""
        if not self.collection:
            return
        
        if doc_id is None:
            doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if metadata is None:
            metadata = {"added_at": datetime.now().isoformat()}
        
        metadata["content"] = content[:500]  # Store preview
        
        try:
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
        except Exception as e:
            print(f"Error adding document: {e}")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search knowledge base."""
        if not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            ids = results.get("ids", [[]])[0]
            
            return [
                {
                    "id": ids[i] if i < len(ids) else "",
                    "content": documents[i] if i < len(documents) else "",
                    "metadata": metadatas[i] if i < len(metadatas) else {}
                }
                for i in range(len(documents))
            ]
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    def get_recent(self, n: int = 10) -> List[Dict]:
        """Get recent documents."""
        if not self.collection:
            return []
        
        try:
            results = self.collection.get()
            docs = results.get("documents", [])
            metas = results.get("metadatas", [])
            ids = results.get("ids", [])
            
            recent = []
            for i in range(len(docs) - 1, max(len(docs) - n - 1, -1), -1):
                if i >= 0:
                    recent.append({
                        "id": ids[i],
                        "content": docs[i],
                        "metadata": metas[i]
                    })
            return recent
        except:
            return []
    
    def delete(self, doc_id: str):
        """Delete a document."""
        if not self.collection:
            return
        
        try:
            self.collection.delete(ids=[doc_id])
        except:
            pass
    
    def count(self) -> int:
        """Count documents."""
        if not self.collection:
            return 0
        return self.collection.count()
    
    def add_from_file(self, file_path: str, category: str = "code"):
        """Add content from a file."""
        path = Path(file_path)
        if not path.exists():
            return
        
        content = path.read_text(encoding="utf-8", errors="ignore")
        
        self.add_document(
            content=content[:5000],  # Limit size
            metadata={
                "source": str(path),
                "category": category,
                "added_at": datetime.now().isoformat()
            }
        )
    
    def add_from_directory(self, dir_path: str, extensions: List[str] = None):
        """Add all files from a directory."""
        if extensions is None:
            extensions = [".py", ".js", ".md", ".txt", ".json"]
        
        path = Path(dir_path)
        if not path.exists():
            return
        
        count = 0
        for ext in extensions:
            for file in path.rglob(f"*{ext}"):
                try:
                    self.add_from_file(str(file), category=ext[1:])
                    count += 1
                except:
                    pass
        
        return count


class MemoryManager:
    """Manager for all memory systems."""
    
    def __init__(self, kb_persist_dir: str = None):
        self.short_term = []  # In-memory short term
        self.long_term = KnowledgeBase(kb_persist_dir)
    
    def add_short_term(self, query: str, response: str):
        """Add to short term memory."""
        self.short_term.append({
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 20
        self.short_term = self.short_term[-20:]
    
    def get_short_term(self, n: int = 10) -> List[Dict]:
        """Get recent short term memories."""
        return self.short_term[-n:]
    
    def retrieve(self, query: str, n: int = 5) -> Dict:
        """Retrieve relevant context."""
        context = {
            "short_term": self.short_term[-n:],
            "long_term": self.long_term.search(query, n),
        }
        return context


def get_knowledge_base(persist_dir: str = None) -> KnowledgeBase:
    """Get knowledge base instance."""
    return KnowledgeBase(persist_dir)


def get_memory_manager() -> MemoryManager:
    """Get memory manager."""
    return MemoryManager()


if __name__ == "__main__":
    print("Knowledge Base")
    kb = get_knowledge_base()
    kb.add_document("Python is a programming language.", {"category": "fact"})
    print(f"Count: {kb.count()}")
    results = kb.search("python")
    print(f"Results: {results}")