"""Passphrase usage tracking model."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base


class PassphraseUsage(Base):
    """Track passphrase usage for access control."""
    __tablename__ = "passphrase_usage"
    
    id = Column(String, primary_key=True)
    passphrase = Column(String, nullable=False, index=True)
    repo_id = Column(String, ForeignKey("repositories.id"), nullable=True)  # NULL means question usage
    questions_asked = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    repository = relationship("Repository", backref="passphrase_usages")

