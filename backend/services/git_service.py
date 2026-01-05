"""Git service for cloning and traversing repositories."""
import os
import tempfile
import shutil
from pathlib import Path
from urllib.parse import urlparse
from git import Repo
from git.exc import GitCommandError
from backend.config import settings


def get_repo_cache_path(repo_url: str) -> Path:
    """
    Get the cache path for a repository.
    
    Args:
        repo_url: URL of the repository
        
    Returns:
        Path to the cached repository directory
    """
    # Parse URL to get repo name
    parsed = urlparse(repo_url)
    # Extract owner/repo from path (e.g., github.com/user/repo -> user-repo)
    path_parts = [p for p in parsed.path.strip('/').split('/') if p]
    if len(path_parts) >= 2:
        repo_name = f"{path_parts[-2]}-{path_parts[-1]}"
    else:
        repo_name = path_parts[-1] if path_parts else "unknown"
    
    # Remove .git suffix if present
    repo_name = repo_name.replace('.git', '')
    
    # Create cache directory path
    cache_path = Path(settings.cache_dir) / repo_name
    return cache_path


def clone_repository(repo_url: str) -> str:
    """
    Clone a Git repository to permanent cache directory.
    Uses existing cache if repository already exists.
    
    Args:
        repo_url: URL of the repository to clone
        
    Returns:
        Path to the cloned repository
        
    Raises:
        GitCommandError: If cloning fails
    """
    cache_path = get_repo_cache_path(repo_url)
    
    # Check if repository already exists in cache
    if cache_path.exists() and (cache_path / '.git').exists():
        # Repository already cached, update it
        try:
            repo = Repo(cache_path)
            repo.remotes.origin.fetch()
            repo.remotes.origin.pull()
            return str(cache_path)
        except Exception as e:
            # If update fails, re-clone
            shutil.rmtree(cache_path, ignore_errors=True)
    
    # Ensure cache directory exists
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Clone repository
    try:
        repo = Repo.clone_from(repo_url, str(cache_path))
        return str(cache_path)
    except GitCommandError as e:
        shutil.rmtree(cache_path, ignore_errors=True)
        raise


def get_folder_structure(repo_path: str, folder_path: str) -> str:
    """
    Get folder structure as a tree-like string for LLM prompts.
    
    Args:
        repo_path: Path to repository root
        folder_path: Path to folder relative to repo root
        
    Returns:
        String representation of folder structure
    """
    full_path = Path(repo_path) / folder_path if folder_path else Path(repo_path)
    
    if not full_path.exists() or not full_path.is_dir():
        return ""
    
    structure_lines = []
    
    # Get all items in folder
    try:
        items = sorted(full_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        
        for item in items:
            # Skip .git and summary files
            if item.name.startswith('.') or item.name.endswith('.md'):
                continue
            
            if item.is_dir():
                structure_lines.append(f"├── {item.name}/")
            else:
                structure_lines.append(f"├── {item.name}")
    except Exception:
        pass
    
    if structure_lines:
        # Replace last ├── with └──
        if structure_lines:
            structure_lines[-1] = structure_lines[-1].replace("├──", "└──")
    
    return "\n".join(structure_lines) if structure_lines else ""


def get_file_tree(repo_path: str) -> list[dict]:
    """
    Get file tree structure from repository.
    
    Args:
        repo_path: Path to the cloned repository
        
    Returns:
        List of file/folder dictionaries with path and type
    """
    repo = Repo(repo_path)
    tree = []
    
    # Get all files tracked by git
    for item in repo.tree().traverse():
        if item.type == "blob":  # File
            tree.append({
                "path": item.path,
                "type": "file",
                "size": item.size if hasattr(item, "size") else 0,
            })
        elif item.type == "tree":  # Folder
            tree.append({
                "path": item.path,
                "type": "folder",
            })
    
    return tree


def read_file_content(file_path: str, max_size: int = None) -> str | None:
    """
    Read file content, respecting size limits.
    
    Args:
        file_path: Path to the file
        max_size: Maximum file size in bytes (defaults to config)
        
    Returns:
        File content or None if file is too large or binary
    """
    if max_size is None:
        max_size = settings.max_file_size
    
    try:
        file_stat = os.stat(file_path)
        if file_stat.st_size > max_size:
            return None
        
        # Try to read as text
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            return content
    except Exception:
        return None


def cleanup_repository(repo_path: str):
    """
    Clean up cloned repository directory.
    
    Note: With permanent caching, this is now a no-op.
    Repositories are kept in cache for reuse.
    """
    # No longer cleaning up - repositories are cached permanently
    pass

