"""Repository schemas."""
from pydantic import BaseModel
from datetime import datetime
from backend.models.repository import RepositoryStatus


class RepositoryCreate(BaseModel):
    """Repository creation schema."""
    url: str


class RepositoryResponse(BaseModel):
    """Repository response schema."""
    id: str
    url: str
    status: RepositoryStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

