"""
AI Coding Agent Brain - Vector Memory (Semantic Search)
======================================================
Uses ChromaDB for embeddings-based semantic memory.
Enables natural language search across your knowledge base.

Features:
- Embeddings for semantic search
- Persistent vector storage
- Natural language queries
- Context-aware retrieval
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("ChromaDB not installed. Run: pip install chromadb")
    raise

BASE_DIR = Path(__file__).parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
EMBEDDINGS_DIR = KNOWLEDGE_DIR / "embeddings"

CHROMA_CLIENT = None
COLLECTION = None


def init_chroma():
    """Initialize ChromaDB client and collection."""
    global CHROMA_CLIENT, COLLECTION
    
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
    
    CHROMA_CLIENT = chromadb.PersistentClient(
        path=str(EMBEDDINGS_DIR),
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    
    COLLECTION = CHROMA_CLIENT.get_or_create_collection(
        name="ai_brain_memory",
        metadata={"description": "AI Coding Agent Knowledge Base"}
    )
    
    return CHROMA_CLIENT, COLLECTION


def get_embedding_model():
    """Get the embedding model - uses Ollama's embeddings if available."""
    try:
        result = subprocess.run(
            ["ollama", "embed", "-m", "nomic-embed-text", "-t", "test"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return "ollama:nomic-embed-text"
    except:
        pass
    
    return None


def create_embeddings(texts: List[str]) -> List[List[float]]:
    """Create embeddings using available models."""
    embeddings = []
    
    for text in texts:
        try:
            result = subprocess.run(
                ["ollama", "embed", "-m", "nomic-embed-text"],
                input=text,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                emb = [float(x) for x in result.stdout.strip().split(',')]
                embeddings.append(emb)
                continue
        except:
            pass
        
        embeddings.append([0.0] * 384)
    
    return embeddings


def add_memory(
    content: str,
    metadata: Optional[Dict] = None,
    memory_id: Optional[str] = None
) -> str:
    """Add a memory to the vector store."""
    global CHROMA_CLIENT, COLLECTION
    
    if COLLECTION is None:
        init_chroma()
    
    memory_id = memory_id or f"memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    meta = metadata or {}
    meta["content"] = content
    meta["timestamp"] = datetime.now().isoformat()
    
    embedding = create_embeddings([content])[0]
    
    COLLECTION.add(
        ids=[memory_id],
        documents=[content],
        metadatas=[meta],
        embeddings=[embedding]
    )
    
    return f"Added memory: {memory_id}"


def search_memory(
    query: str,
    n_results: int = 5,
    filter_metadata: Optional[Dict] = None
) -> List[Dict]:
    """Search memories using semantic similarity."""
    global CHROMA_CLIENT, COLLECTION
    
    if COLLECTION is None:
        init_chroma()
    
    query_embedding = create_embeddings([query])[0]
    
    results = COLLECTION.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=filter_metadata,
        include=["documents", "metadatas", "distances"]
    )
    
    memories = []
    if results["documents"] and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            memories.append({
                "content": doc,
                "id": results["ids"][0][i],
                "distance": results["distances"][0][i],
                "metadata": results["metadatas"][0][i]
            })
    
    return memories


def recall_similar(context: str, n: int = 3) -> str:
    """Recall similar memories to given context."""
    memories = search_memory(context, n)
    
    if not memories:
        return "No similar memories found."
    
    result = f"Found {len(memories)} similar memories:\n\n"
    for i, mem in enumerate(memories, 1):
        similarity = (1 - mem["distance"]) * 100
        result += f"{i}. {mem['content'][:200]}...\n"
        result += f"   Similarity: {similarity:.1f}%\n\n"
    
    return result


def get_memory_stats() -> Dict:
    """Get statistics about stored memories."""
    global CHROMA_CLIENT, COLLECTION
    
    if COLLECTION is None:
        return {"total": 0}
    
    return {
        "total": COLLECTION.count(),
        "collection": "ai_brain_memory"
    }


def delete_memory(memory_id: str) -> str:
    """Delete a specific memory."""
    global CHROMA_CLIENT, COLLECTION
    
    if COLLECTION is None:
        return "No memories stored."
    
    COLLECTION.delete(ids=[memory_id])
    return f"Deleted memory: {memory_id}"


def clear_all_memories() -> str:
    """Clear all stored memories."""
    global CHROMA_CLIENT, COLLECTION
    
    if COLLECTION is None:
        return "No memories to clear."
    
    CHROMA_CLIENT.delete_collection("ai_brain_memory")
    COLLECTION = CHROMA_CLIENT.get_or_create_collection(
        name="ai_brain_memory"
    )
    return "Cleared all memories."


def ingest_knowledge_directory():
    """Ingest all markdown files from knowledge directory into vector store."""
    global CHROMA_CLIENT, COLLECTION
    
    if COLLECTION is None:
        init_chroma()
    
    markdown_files = list(KNOWLEDGE_DIR.rglob("*.md"))
    added = 0
    
    for md_file in markdown_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            if len(content) > 10:
                add_memory(
                    content=content,
                    metadata={
                        "source": str(md_file),
                        "type": "knowledge"
                    },
                    memory_id=f"file_{md_file.stem}"
                )
                added += 1
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return f"Ingested {added} knowledge files."


def semantic_search(query: str, use_natural: bool = True) -> str:
    """
    Perform semantic search on knowledge base.
    
    Args:
        query: Search query
        use_natural: If True, uses natural language matching
    
    Returns:
        Formatted search results
    """
    if use_natural:
        return recall_similar(query)
    else:
        return search_memory(query, n_results=5)


class SemanticMemory:
    """Semantic memory wrapper for easy integration."""
    
    def __init__(self):
        init_chroma()
    
    def remember(self, content: str, metadata: Optional[Dict] = None) -> str:
        """Store a memory."""
        return add_memory(content, metadata)
    
    def recall(self, context: str, n: int = 3) -> str:
        """Recall similar memories."""
        return recall_similar(context, n)
    
    def stats(self) -> Dict:
        """Get memory statistics."""
        return get_memory_stats()
    
    def clear(self) -> str:
        """Clear all memories."""
        return clear_all_memories()


if __name__ == "__main__":
    print("=" * 60)
    print("🧠 Vector Semantic Memory")
    print("=" * 60)
    
    init_chroma()
    
    print("\nIngesting knowledge files...")
    result = ingest_knowledge_directory()
    print(result)
    
    print("\nMemory stats:")
    stats = get_memory_stats()
    print(f"Total memories: {stats['total']}")
    
    print("\n" + "=" * 60)
    print("Semantic Memory Ready!")
    print("=" * 60)