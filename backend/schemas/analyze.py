"""Analyze endpoint schemas."""
from pydantic import BaseModel, HttpUrl


class AnalyzeRequest(BaseModel):
    """Analyze request schema (matches OpenAPI)."""
    repo_url: HttpUrl
    depth: int = 3
    passphrase: str  # Required passphrase for access control


class AnalyzeResponse(BaseModel):
    """Analyze response schema (matches OpenAPI)."""
    task_id: str

