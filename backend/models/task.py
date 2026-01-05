"""Task model for async processing."""
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
import enum
from backend.db.base import Base


class TaskStatus(str, enum.Enum):
    """Task status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(Base):
    """Task model for async repository analysis."""
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True)
    repo_id = Column(String, ForeignKey("repositories.id"), nullable=False)
    status = Column(String, default=TaskStatus.PENDING.value)
    progress = Column(Integer, default=0)  # 0-100
    status_message = Column(Text, nullable=True)  # Detailed status message
    error_message = Column(Text, nullable=True)
    result_id = Column(String, nullable=True)  # Repository ID when completed
    
    # Relationships
    repository = relationship("Repository", backref="tasks")

