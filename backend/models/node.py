"""Node model for repository tree."""
from sqlalchemy import Column, String, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Float
from sqlalchemy.orm import relationship
import enum
from backend.db.base import Base
from backend.config import settings


class NodeType(str, enum.Enum):
    """Node type."""
    FILE = "file"
    FOLDER = "folder"


class Node(Base):
    """Repository node (file or folder) model."""
    __tablename__ = "nodes"
    
    id = Column(String, primary_key=True)
    repo_id = Column(String, ForeignKey("repositories.id"), nullable=False)
    parent_id = Column(String, ForeignKey("nodes.id"), nullable=True)
    path = Column(String, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "file" or "folder"
    summary = Column(Text, nullable=True)
    # Use PostgreSQL ARRAY for embeddings (JSON for SQLite fallback)
    embedding = Column(
        ARRAY(Float) if "postgresql" in settings.database_url.lower() else JSON,
        nullable=True
    )
    
    # Relationships
    parent = relationship("Node", remote_side=[id], backref="children")
    repository = relationship("Repository", backref="nodes")

