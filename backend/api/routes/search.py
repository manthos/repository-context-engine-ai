"""Search endpoint."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.schemas.search import SearchResult
from backend.db.base import get_db
from backend.models.node import Node
from backend.services.embedding_service import search_summaries
from typing import List

router = APIRouter()


@router.get("/search", response_model=List[SearchResult])
async def search(
    q: str = Query(..., description="Search query"),
    repo_id: str = Query(None, description="Repository ID to filter results"),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
):
    """Hybrid search across code summaries."""
    results = search_summaries(db, q, limit, repo_id=repo_id)
    
    return [
        SearchResult(
            path=result["path"],
            score=result["score"],
            summary_snippet=result["summary_snippet"],
        )
        for result in results
    ]

