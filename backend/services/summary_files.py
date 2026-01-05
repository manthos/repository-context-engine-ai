"""Helper functions for managing summary files in repository cache."""
import os
from pathlib import Path


def get_summary_file_path(repo_path: str, item_path: str, item_type: str, repo_name: str = None) -> Path:
    """
    Get the path to the summary file for an item.
    
    Args:
        repo_path: Path to the repository root
        item_path: Path to the file/folder relative to repo root
        item_type: "file" or "folder"
        repo_name: Repository name (for root summary naming)
        
    Returns:
        Path to the summary .md file
    """
    repo_root = Path(repo_path)
    
    if item_type == "file":
        # For files: <file>.md alongside the original file
        file_path = repo_root / item_path
        return file_path.parent / f"{file_path.name}.md"
    else:
        # For folders: <folder>.md in parent directory (or <repo>.md for root)
        if not item_path:
            # Root folder: <repository>.md at repo root
            if repo_name:
                return repo_root / f"{repo_name}.md"
            else:
                # Fallback to README.md if repo_name not provided
                return repo_root / "README.md"
        else:
            # Subfolder: <folder>.md in parent directory
            folder_path = repo_root / item_path
            folder_name = folder_path.name
            parent_dir = folder_path.parent
            return parent_dir / f"{folder_name}.md"


def summary_exists(repo_path: str, item_path: str, item_type: str, repo_name: str = None) -> bool:
    """Check if a summary file already exists."""
    summary_path = get_summary_file_path(repo_path, item_path, item_type, repo_name)
    return summary_path.exists()


def read_summary(repo_path: str, item_path: str, item_type: str, repo_name: str = None) -> str | None:
    """Read an existing summary from file."""
    summary_path = get_summary_file_path(repo_path, item_path, item_type, repo_name)
    if summary_path.exists():
        try:
            return summary_path.read_text(encoding="utf-8")
        except Exception:
            return None
    return None


def write_summary(repo_path: str, item_path: str, item_type: str, summary: str, repo_name: str = None):
    """Write a summary to file."""
    summary_path = get_summary_file_path(repo_path, item_path, item_type, repo_name)
    # Ensure parent directory exists
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(summary, encoding="utf-8")

