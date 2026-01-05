"""Unit tests for embedding service."""
import pytest
from backend.services.embedding_service import create_embedding


def test_create_embedding():
    """Test embedding creation."""
    text = "Test content for embedding"
    embedding = create_embedding(text)
    
    # Should return None for SQLite or a list for Postgres
    assert embedding is None or isinstance(embedding, list)

