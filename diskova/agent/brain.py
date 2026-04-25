"""
Processing (Brain) Layer
========================
Core reasoning engine - LLM, NLP, Memory, Reasoning.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class NLProcessor:
    """Natural Language Processing."""
    
    def __init__(self):
        pass
    
    def parse(self, text: str) -> Dict:
        """Parse input to find intent and entities."""
        text = text.lower().strip()
        
        intents = []
        entities = {}
        
        # Intent detection
        if any(w in text for w in ["hello", "hi", "hey", "greet"]):
            intents.append("greeting")
        if any(w in text for w in ["write", "code", "create", "make"]):
            intents.append("create")
        if any(w in text for w in ["search", "find", "look"]):
            intents.append("search")
        if any(w in text for w in ["explain", "what", "how"]):
            intents.append("information")
        if any(w in text for w in ["debug", "fix", "error"]):
            intents.append("debug")
        
        # Entity extraction (simple)
        import re
        emails = re.findall(r'[\w.-]+@[\w.-]+', text)
        if emails:
            entities["email"] = emails[0]
        
        urls = re.findall(r'http[^\s]+', text)
        if urls:
            entities["url"] = urls[0]
        
        return {
            "text": text,
            "intents": intents or ["general"],
            "entities": entities,
            "original": text
        }


class Reasoner:
    """Reasoning and planning engine."""
    
    def __init__(self):
        self.steps = []
    
    def plan(self, intent: str, context: Dict) -> List[str]:
        """Determine steps to fulfill request."""
        plans = {
            "create": ["1. Validate request", "2. Write code", "3. Test output"],
            "search": ["1. Parse query", "2. Search knowledge", "3. Return results"],
            "debug": ["1. Analyze error", "2. Find root cause", "3. Propose fix"],
            "information": ["1. Search web/docs", "2. Synthesize answer"],
            "greeting": ["1. Acknowledge", "2. Offer help"],
        }
        self.steps = plans.get(intent, ["1. Process request"])
        return self.steps
    
    def execute(self) -> str:
        """Get current step."""
        return " -> ".join(self.steps)


class ShortTermMemory:
    """Working memory for current conversation."""
    
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.history: List[Dict] = []
    
    def add(self, role: str, content: str, metadata: Dict = None):
        """Add message to memory."""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        
        if len(self.history) > self.max_turns:
            self.history = self.history[-self.max_turns:]
    
    def get_context(self, last_n: int = 5) -> List[Dict]:
        """Get recent context."""
        return self.history[-last_n:]
    
    def get_messages(self) -> List[Dict]:
        """Get all messages for LLM."""
        return self.history
    
    def clear(self):
        """Clear memory."""
        self.history = []


class LongTermMemory:
    """Vector database for persistent memory."""
    
    def __init__(self):
        self.chroma_client = None
        self.collection = None
    
    def init(self, persist_dir: str = "./data/memory"):
        """Initialize vector store."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            os.makedirs(persist_dir, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.chroma_client.get_or_create_collection("memory")
            return True
        except:
            return False
    
    def store(self, key: str, content: str, metadata: Dict = None):
        """Store memory."""
        if not self.collection:
            return False
        
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            import hashlib
            
            # Simple hash as ID
            doc_id = hashlib.md5(content.encode()).hexdigest()
            
            self.collection.add(
                ids=[doc_id],
                documents=[content],
                metadatas=[metadata or {"key": key}]
            )
            return True
        except:
            return False
    
    def recall(self, query: str, top_k: int = 3) -> List[str]:
        """Search memories."""
        if not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            docs = results.get("documents", [[]])
            return docs[0] if docs and len(docs) > 0 else []
        except:
            return []


class Brain:
    """Main processing engine."""
    
    def __init__(self):
        self.nlp = NLProcessor()
        self.reasoner = Reasoner()
        self.short_memory = ShortTermMemory()
        self.long_memory = LongTermMemory()
    
    def init_long_memory(self, persist_dir: str = "./data/memory"):
        """Initialize persistent memory."""
        return self.long_memory.init(persist_dir)
    
    def process(self, text: str) -> Dict:
        """Process input: parse, plan, execute."""
        # Parse intent
        parsed = self.nlp.parse(text)
        
        # Plan steps
        plan = self.reasoner.plan(parsed["intents"][0], parsed)
        
        # Add to short memory
        self.short_memory.add("user", text, parsed)
        
        return {
            "parsed": parsed,
            "plan": plan,
            "context": self.short_memory.get_context()
        }
    
    def generate_prompt(self) -> List[Dict]:
        """Generate messages for LLM with context."""
        messages = []
        
        # System prompt
        messages.append({
            "role": "system",
            "content": "You are Diskova AI, a helpful coding assistant. Be concise and accurate."
        })
        
        # Conversation history
        for msg in self.short_memory.get_messages():
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return messages


def get_brain() -> Brain:
    """Get brain instance."""
    return Brain()


if __name__ == "__main__":
    print("Processing (Brain) Layer")
    brain = get_brain()
    
    # Test NLP
    result = brain.process("Write hello world in python")
    print(f"Intent: {result['parsed']['intents']}")
    print(f"Plan: {result['plan']}")
    print(f"Memory: {len(brain.short_memory.history)} items")