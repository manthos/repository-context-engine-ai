"""Browse endpoint for viewing repository cache summaries."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.db.base import get_db
from backend.models.repository import Repository
from backend.services.git_service import get_repo_cache_path
from backend.services.summary_files import get_summary_file_path, read_summary
from pathlib import Path
from backend.config import settings

router = APIRouter()


def secure_path_join(base: Path, *parts: str) -> Path:
    """
    Securely join paths, preventing directory traversal attacks.
    
    Args:
        base: Base directory (cache root)
        *parts: Path components
        
    Returns:
        Resolved path if within base, raises HTTPException otherwise
    """
    # Resolve base to absolute path
    base = base.resolve()
    
    # Join and resolve the target path
    target = base
    for part in parts:
        if part == ".." or part.startswith("/"):
            raise HTTPException(status_code=400, detail="Invalid path")
        target = target / part
    
    # Resolve to absolute path
    target = target.resolve()
    
    # Ensure target is within base (prevents directory traversal)
    try:
        target.relative_to(base)
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied: path outside cache directory")
    
    return target


@router.get("/browse/{repo_id}")
async def browse_repository(
    repo_id: str,
    path: str = Query("", description="Path within repository (empty for root)"),
    db: Session = Depends(get_db),
):
    """
    Browse repository cache summaries.
    
    Returns file/folder structure and summary content.
    """
    try:
        # Get repository
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Get cache path
        cache_path = get_repo_cache_path(repo.url)
        if not cache_path.exists():
            raise HTTPException(status_code=404, detail="Repository cache not found")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error getting repository: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error accessing repository: {str(e)}")
    
    # Secure path resolution
    try:
        if path:
            # Filter out empty strings from split
            path_parts = [p for p in path.split("/") if p]
            target_path = secure_path_join(cache_path, *path_parts) if path_parts else cache_path
        else:
            target_path = cache_path
    except HTTPException as e:
        raise
    except Exception as e:
        import traceback
        print(f"Error resolving path '{path}': {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error resolving path: {str(e)}")
    
    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Path not found")
    
    # Get repository name for summary file lookup
    repo_name = cache_path.name
    
    # If it's a directory, list contents
    if target_path.is_dir():
        items = []
        try:
            # Get all items first to check for summary files
            all_items = list(target_path.iterdir())
            
            for item in sorted(all_items):
                # Skip .git directory and hidden files/folders
                if item.name.startswith('.'):
                    if item.is_dir() and item.name == '.git':
                        continue
                    # Skip hidden items
                    continue
                
                # Skip summary .md files (they're metadata, not files to browse)
                # Summary files can be:
                # 1. File summaries: <filename>.md where <filename> exists as another file
                # 2. Folder summaries: <foldername>.md where <foldername> exists as a folder
                # 3. Root summary: <repo-name>.md (shown in folder summary section, not as file)
                # Original .md files (like README.md) should still be shown
                if item.is_file() and item.name.endswith('.md'):
                    # Special case: Root summary file (<repo-name>.md) should be hidden
                    root_summary_name = f"{repo_name}.md"
                    if item.name == root_summary_name:
                        continue  # Skip root summary (shown in folder summary section)
                    
                    # Remove .md extension to get base name
                    base_name = item.name[:-3]  # Remove .md extension
                    
                    # Check if this is a file summary: does a file with this name exist?
                    # This includes checking for .md files too (e.g., README.md.md is summary of README.md)
                    is_file_summary = False
                    for other_item in all_items:
                        if (other_item != item and 
                            other_item.is_file() and
                            other_item.name == base_name):
                            # Found matching file - this .md is a summary
                            # Exception: don't match if the other file is also a summary file (ends with .md.md)
                            # A summary file would be like README.md.md, so check if it ends with .md.md
                            other_is_summary_file = other_item.name.endswith('.md.md')
                            if not other_is_summary_file:
                                is_file_summary = True
                                break
                    
                    # Check if this is a folder summary: does a folder with this name exist?
                    is_folder_summary = False
                    for other_item in all_items:
                        if (other_item != item and 
                            other_item.is_dir() and
                            other_item.name == base_name):
                            is_folder_summary = True
                            break
                    
                    # Skip if it's either a file summary or folder summary
                    if is_file_summary or is_folder_summary:
                        continue  # Skip summary files
                
                try:
                    item_path = item.relative_to(cache_path)
                    item_type = "folder" if item.is_dir() else "file"
                    
                    # Check for summary file
                    has_summary = False
                    if item_type == "file":
                        # Check if there's a summary file: <filename>.md
                        summary_path = get_summary_file_path(str(cache_path), str(item_path), "file", repo_name)
                        has_summary = summary_path.exists()
                    else:  # folder
                        # Check if there's a folder summary: <foldername>.md in parent directory
                        summary_path = get_summary_file_path(str(cache_path), str(item_path), "folder", repo_name)
                        has_summary = summary_path.exists()
                    
                    items.append({
                        "name": item.name,
                        "type": item_type,
                        "path": str(item_path),
                        "has_summary": has_summary,
                    })
                except (ValueError, Exception) as e:
                    # Log the error for debugging
                    import traceback
                    print(f"Warning: Could not process item {item.name} in {target_path}: {e}")
                    print(traceback.format_exc())
                    # Try to add it anyway with basic info using the path from current directory
                    try:
                        # Use path relative to current target_path instead of cache_path
                        if path:
                            relative_path = f"{path}/{item.name}" if path else item.name
                        else:
                            relative_path = item.name
                        
                        items.append({
                            "name": item.name,
                            "type": "folder" if item.is_dir() else "file",
                            "path": relative_path,
                            "has_summary": False,
                        })
                    except Exception as e2:
                        # If even that fails, skip it
                        print(f"Could not add item {item.name} even with fallback: {e2}")
                        continue
        except PermissionError:
            raise HTTPException(status_code=403, detail="Permission denied")
        except Exception as e:
            # Log the error and return empty list
            import traceback
            print(f"Error listing directory {target_path}: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error listing directory: {str(e)}")
        
        # Also check for folder summary if this is a folder
        folder_summary = None
        if path:  # Not root
            try:
                folder_summary_path = get_summary_file_path(str(cache_path), path, "folder", repo_name)
                if folder_summary_path.exists():
                    try:
                        folder_summary = folder_summary_path.read_text(encoding="utf-8")
                    except Exception:
                        pass
            except Exception:
                pass
        
        # Check for root summary if at root
        root_summary = None
        if not path:
            try:
                root_summary_path = get_summary_file_path(str(cache_path), "", "folder", repo_name)
                if root_summary_path.exists():
                    try:
                        root_summary = root_summary_path.read_text(encoding="utf-8")
                    except Exception:
                        pass
            except Exception:
                pass
        
        # Add parent folder navigation if not at root
        if path:
            # Calculate parent path
            path_parts = [p for p in path.split("/") if p]
            if path_parts:
                path_parts.pop()
                parent_path = "/".join(path_parts) if path_parts else ""
            else:
                parent_path = ""
            
            # Add parent folder entry at the beginning
            items.insert(0, {
                "name": "..",
                "type": "folder",
                "path": parent_path,
                "has_summary": False,
            })
        
        return {
            "type": "folder",
            "path": path or "/",
            "items": items,
            "summary": folder_summary or root_summary,
        }
    
    # If it's a file, return file content and summary
    else:
        # Read file content (if text file)
        file_content = None
        try:
            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                file_content = f.read()
        except Exception:
            file_content = None
        
        # Get summary from corresponding .md file
        # Use the path parameter directly since target_path was constructed from it
        file_path_str = path  # path parameter is already relative to repo root
        
        summary_path = get_summary_file_path(str(cache_path), file_path_str, "file", repo_name)
        summary_exists = False
        summary = None
        if summary_path.exists():
            try:
                summary = summary_path.read_text(encoding="utf-8")
                summary_exists = True
            except Exception:
                pass
        
        return {
            "type": "file",
            "path": file_path_str,
            "name": target_path.name,
            "content": file_content,
            "summary": summary,
            "summary_exists": summary_exists,
        }

