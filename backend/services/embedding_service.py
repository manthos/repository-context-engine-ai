"""Embedding service for vector search."""
from sqlalchemy.orm import Session
from backend.models.node import Node
from backend.config import settings
from typing import List, Dict
import numpy as np


def create_embedding(text: str) -> List[float] | None:
    """
    Create embedding for text.
    
    Note: This is a placeholder. In production, use a proper embedding model
    like OpenAI's text-embedding-ada-002 or sentence-transformers.
    """
    # For MVP, return None if pgvector not available
    # In production, implement proper embedding generation
    if "sqlite" in settings.database_url.lower():
        return None
    
    # Placeholder: return simple hash-based "embedding" for testing
    # Replace with actual embedding model in production
    import hashlib
    hash_obj = hashlib.md5(text.encode())
    hash_hex = hash_obj.hexdigest()
    # Convert to 128-dim vector (simple hash-based)
    embedding = [float(int(c, 16)) / 15.0 for c in hash_hex[:128]]
    return embedding


def search_summaries(db: Session, query: str, limit: int = 10, repo_id: str = None) -> List[Dict]:
    """
    Search summaries using vector similarity or text matching.
    
    Args:
        db: Database session
        query: Search query
        limit: Maximum number of results
        repo_id: Optional repository ID to filter results
        
    Returns:
        List of search results with path, score, and summary_snippet
    """
    # Simple text-based search for MVP
    # In production with pgvector, use vector similarity search
    query_filter = db.query(Node).filter(
        Node.summary.isnot(None),
        Node.summary.contains(query)
    )
    
    # Filter by repository if provided
    if repo_id:
        query_filter = query_filter.filter(Node.repo_id == repo_id)
    
    nodes = query_filter.limit(limit * 2).all()  # Get more to score and sort
    
    results = []
    query_lower = query.lower()
    query_words = query_lower.split()
    
    for node in nodes:
        summary_lower = node.summary.lower() if node.summary else ""
        
        # Calculate relevance score
        # Exact phrase match = highest score
        if query_lower in summary_lower:
            score = 2.0
        # All words present = high score
        elif all(word in summary_lower for word in query_words if len(word) > 2):
            score = 1.5
        # Some words present = medium score
        elif any(word in summary_lower for word in query_words if len(word) > 2):
            score = 1.0
        else:
            score = 0.5
        
        # Boost score for file paths that match query
        if query_lower in node.path.lower():
            score += 0.5
        
        results.append({
            "path": node.path,
            "score": score,
            "summary_snippet": node.summary[:300] if node.summary else "",
        })
    
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results[:limit]

