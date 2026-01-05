"""Analyze endpoint."""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from backend.db.base import get_db
from backend.services.analyzer import start_analysis
from backend.services.github_service import get_repository_size
from backend.services.passphrase_service import can_crawl_repository, record_repository_crawl
from backend.config import settings
import uuid

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse, status_code=202)
async def analyze_repo(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Start recursive analysis of a Git repository."""
    repo_url = str(request.repo_url)
    
    # Check passphrase and access limits
    can_crawl, error_msg = can_crawl_repository(db, request.passphrase)
    if not can_crawl:
        raise HTTPException(status_code=403, detail=error_msg)
    
    # Check repository size limit before starting analysis
    if settings.max_git_size_kb > 0:
        size_kb = await get_repository_size(repo_url)
        
        if size_kb is not None and size_kb > settings.max_git_size_kb:
            error_msg = (
                f"This demo version limits repository size to {settings.max_git_size_kb}KB. "
                f"The repository '{repo_url}' is {size_kb}KB. "
                f"Please use a smaller repository for testing. "
                f"You can find small repositories at: "
                f"https://github.com/search?q=size%3A10&type=repositories&ref=advsearch"
            )
            raise HTTPException(status_code=400, detail=error_msg)
    
    task_id = str(uuid.uuid4())
    
    # Start analysis in background
    # Pass passphrase to record usage after successful analysis
    background_tasks.add_task(
        start_analysis, 
        task_id, 
        repo_url, 
        request.depth, 
        db,
        request.passphrase  # Pass passphrase to record usage
    )
    
    return AnalyzeResponse(task_id=task_id)

