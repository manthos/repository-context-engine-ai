"""Search endpoint schemas."""
from pydantic import BaseModel
from typing import List


class SearchRequest(BaseModel):
    """Search request schema."""
    q: str


class SearchResult(BaseModel):
    """Search result schema (matches OpenAPI)."""
    path: str
    score: float
    summary_snippet: str

