"""Node model for repository tree."""
from sqlalchemy import Column, String, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Float, TypeDecorator
from sqlalchemy.orm import relationship
import enum
import json
from backend.db.base import Base


class JSONEncodedArray(TypeDecorator):
    """
    Custom type that stores arrays as JSON for SQLite compatibility.
    Uses native PostgreSQL ARRAY for PostgreSQL.
    """
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(ARRAY(Float))
        else:
            return dialect.type_descriptor(JSON)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        # For SQLite, ensure it's serialized as JSON
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        # For SQLite, it comes back as a list already
        return value


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
    # Use custom type that adapts to database dialect
    embedding = Column(JSONEncodedArray, nullable=True)
    
    # Relationships
    parent = relationship("Node", remote_side=[id], backref="children")
    repository = relationship("Repository", backref="nodes")

