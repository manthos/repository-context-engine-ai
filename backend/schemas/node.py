"""Node schemas."""
from pydantic import BaseModel
from typing import List, Optional


class NodeResponse(BaseModel):
    """Node response schema."""
    id: str
    repo_id: str
    parent_id: Optional[str]
    path: str
    name: str
    type: str
    summary: Optional[str]
    
    class Config:
        from_attributes = True


class RepoNode(BaseModel):
    """Recursive repository node schema (matches OpenAPI)."""
    name: str
    type: str  # "file" or "folder"
    path: str
    summary: str
    children: List["RepoNode"] = []
    
    class Config:
        from_attributes = True

