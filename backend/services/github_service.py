"""GitHub API service for repository metadata."""
import re
import httpx
from typing import Optional, Tuple


def parse_github_url(repo_url: str) -> Optional[Tuple[str, str]]:
    """
    Parse GitHub repository URL to extract owner and repo name.
    
    Args:
        repo_url: GitHub repository URL (e.g., https://github.com/owner/repo)
        
    Returns:
        Tuple of (owner, repo) or None if URL is invalid
    """
    # Match various GitHub URL formats
    patterns = [
        r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$',
        r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, repo_url)
        if match:
            owner = match.group(1)
            repo = match.group(2).rstrip('/')
            return (owner, repo)
    
    return None


async def get_repository_size(repo_url: str) -> Optional[int]:
    """
    Get repository size from GitHub API (in KB).
    
    Args:
        repo_url: GitHub repository URL
        
    Returns:
        Repository size in KB, or None if unable to determine
    """
    parsed = parse_github_url(repo_url)
    if not parsed:
        return None
    
    owner, repo = parsed
    
    # GitHub API endpoint
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                # GitHub API returns size in KB
                return data.get('size')
            elif response.status_code == 404:
                # Repository not found or private (without auth)
                return None
            else:
                # Other errors (rate limit, etc.)
                return None
    except Exception:
        # Network errors or other issues
        return None



