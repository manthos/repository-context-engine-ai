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
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse, status_code=202)
async def analyze_repo(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Start recursive analysis of a Git repository."""
    logger.info(f"=== ANALYZE REQUEST RECEIVED ===")
    logger.info(f"Repository URL: {request.repo_url}")
    logger.info(f"Depth: {request.depth}")
    logger.info(f"Passphrase provided: {'Yes' if request.passphrase else 'No'}")
    
    repo_url = str(request.repo_url)
    
    # Check passphrase and access limits
    logger.info(f"Checking passphrase and access limits...")
    can_crawl, error_msg = can_crawl_repository(db, request.passphrase)
    if not can_crawl:
        logger.warning(f"Access denied: {error_msg}")
        raise HTTPException(status_code=403, detail=error_msg)
    logger.info(f"Passphrase verified, access granted")
    
    # Check repository size limit before starting analysis
    if settings.max_git_size_kb > 0:
        logger.info(f"Checking repository size (limit: {settings.max_git_size_kb}KB)...")
        size_kb = await get_repository_size(repo_url)
        logger.info(f"Repository size: {size_kb}KB")
        
        if size_kb is not None and size_kb > settings.max_git_size_kb:
            error_msg = (
                f"This demo version limits repository size to {settings.max_git_size_kb}KB. "
                f"The repository '{repo_url}' is {size_kb}KB. "
                f"Please use a smaller repository for testing. "
                f"You can find small repositories at: "
                f"https://github.com/search?q=size%3A10&type=repositories&ref=advsearch"
            )
            logger.warning(f"Repository too large: {size_kb}KB > {settings.max_git_size_kb}KB")
            raise HTTPException(status_code=400, detail=error_msg)
    
    task_id = str(uuid.uuid4())
    logger.info(f"Generated task_id: {task_id}")
    
    # Start analysis in background
    # Pass passphrase to record usage after successful analysis
    logger.info(f"Adding background task for analysis...")
    background_tasks.add_task(
        start_analysis,
        task_id=task_id,
        repo_url=repo_url,
        depth=request.depth or 10,
        db=db,
        passphrase=request.passphrase
    )
    
    logger.info(f"Background task added successfully, returning task_id: {task_id}")
    logger.info(f"=== ANALYZE REQUEST COMPLETED ===")
    return AnalyzeResponse(task_id=task_id)
        start_analysis, 
        task_id, 
        repo_url, 
        request.depth, 
        db,
        request.passphrase  # Pass passphrase to record usage
    )
    
    return AnalyzeResponse(task_id=task_id)

