"""Cache browser endpoint - list all cached repositories."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.base import get_db
from backend.models.repository import Repository
from backend.services.git_service import get_repo_cache_path
from pathlib import Path
from backend.config import settings

router = APIRouter()


@router.get("/cache")
async def list_cached_repositories(db: Session = Depends(get_db)):
    """
    List all cached repositories.
    
    Returns repositories that exist both in database and cache directory.
    """
    cache_dir = Path(settings.cache_dir)
    
    if not cache_dir.exists():
        return {"repositories": []}
    
    # Get all repositories from database
    repos = db.query(Repository).all()
    
    cached_repos = []
    for repo in repos:
        try:
            cache_path = get_repo_cache_path(repo.url)
            if cache_path.exists() and (cache_path / ".git").exists():
                # Get status as string
                if hasattr(repo.status, 'value'):
                    status_str = repo.status.value
                elif isinstance(repo.status, str):
                    status_str = repo.status
                else:
                    status_str = str(repo.status)
                
                # Get relative path, fallback to absolute if not relative
                try:
                    cache_path_str = str(cache_path.relative_to(Path.cwd()))
                except ValueError:
                    # If not relative to cwd, use absolute path
                    cache_path_str = str(cache_path)
                
                cached_repos.append({
                    "id": repo.id,
                    "url": repo.url,
                    "status": status_str,
                    "cache_path": cache_path_str,
                })
        except Exception as e:
            # Skip repos with errors, log if needed
            continue
    
    return {"repositories": cached_repos}

