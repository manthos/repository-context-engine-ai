"""Task schemas."""
from pydantic import BaseModel
from typing import Optional
from backend.models.task import TaskStatus


class TaskCreate(BaseModel):
    """Task creation schema."""
    repo_id: str


class TaskStatus(BaseModel):
    """Task status schema (matches OpenAPI)."""
    status: str  # "pending", "processing", "completed", "failed"
    progress: int  # 0-100
    status_message: Optional[str] = None  # Detailed status message
    result_id: Optional[str] = None


class TaskResponse(BaseModel):
    """Task response schema."""
    id: str
    repo_id: str
    status: TaskStatus
    progress: int
    error_message: Optional[str] = None
    result_id: Optional[str] = None
    
    class Config:
        from_attributes = True

