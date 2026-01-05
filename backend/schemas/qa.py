"""Q&A endpoint schemas."""
from pydantic import BaseModel
from typing import List


class QARequest(BaseModel):
    """Q&A request schema."""
    repo_id: str
    question: str
    passphrase: str  # Required passphrase for access control


class QAResponse(BaseModel):
    """Q&A response schema."""
    answer: str
    sources: List[str]

