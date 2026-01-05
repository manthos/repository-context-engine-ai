"""Repository model."""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from backend.db.base import Base


class RepositoryStatus(str, enum.Enum):
    """Repository analysis status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Repository(Base):
    """Repository model."""
    __tablename__ = "repositories"
    
    id = Column(String, primary_key=True)
    url = Column(String, nullable=False, unique=True)
    status = Column(SQLEnum(RepositoryStatus), default=RepositoryStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

