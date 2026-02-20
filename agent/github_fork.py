"""GitHub fork detection and auto-fork for non-owned repositories."""
import time
import urllib.request
import urllib.error
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.config import GITHUB_TOKEN


def _api_get(url: str, token: str) -> dict | None:
    """Make authenticated GitHub API GET request."""
    if not token:
        return None
    try:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"token {token}")
        req.add_header("Accept", "application/vnd.github.v3+json")
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def _api_post(url: str, token: str, data: dict | None = None) -> dict | None:
    """Make authenticated GitHub API POST request."""
    if not token:
        return None
    try:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"token {token}")
        req.add_header("Accept", "application/vnd.github.v3+json")
        req.add_header("Content-Type", "application/json")
        if data:
            req.data = json.dumps(data).encode()
        req.get_method = lambda: "POST"
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def get_authenticated_user(token: str) -> str | None:
    """Get GitHub username of authenticated user."""
    data = _api_get("https://api.github.com/user", token)
    return data.get("login") if data else None


def parse_repo_url(repo_url: str) -> tuple[str, str] | None:
    """Parse GitHub repo URL into (owner, repo_name)."""
    # Handle: https://github.com/owner/repo or https://github.com/owner/repo.git
    repo_url = repo_url.rstrip("/").replace(".git", "")
    if "github.com" not in repo_url:
        return None
    parts = repo_url.split("github.com/")
    if len(parts) != 2:
        return None
    owner_repo = parts[1].split("/")
    if len(owner_repo) < 2:
        return None
    return owner_repo[0], owner_repo[1]


def check_repo_ownership(repo_url: str, token: str) -> tuple[bool, str | None]:
    """
    Check if authenticated user owns the repo.
    Returns: (is_owner, fork_url_if_needed)
    """
    if not token:
        return False, None  # No token = assume not owner, but can't fork
    
    user = get_authenticated_user(token)
    if not user:
        return False, None
    
    parsed = parse_repo_url(repo_url)
    if not parsed:
        return False, None
    
    owner, repo_name = parsed
    
    # If user owns repo, no fork needed
    if owner.lower() == user.lower():
        return True, None
    
    # Check if fork already exists
    fork_url = f"https://api.github.com/repos/{user}/{repo_name}"
    fork_data = _api_get(fork_url, token)
    if fork_data and not fork_data.get("archived"):
        return False, f"https://github.com/{user}/{repo_name}.git"
    
    # Need to fork
    return False, None


def fork_repository(repo_url: str, token: str) -> str | None:
    """
    Fork a repository via GitHub API.
    Returns: fork_repo_url or None if failed.
    """
    if not token:
        return None
    
    parsed = parse_repo_url(repo_url)
    if not parsed:
        return None
    
    owner, repo_name = parsed
    user = get_authenticated_user(token)
    if not user:
        return None
    
    # Check if fork already exists
    fork_check = _api_get(f"https://api.github.com/repos/{user}/{repo_name}", token)
    if fork_check and not fork_check.get("archived"):
        return f"https://github.com/{user}/{repo_name}.git"
    
    # Create fork
    fork_api_url = f"https://api.github.com/repos/{owner}/{repo_name}/forks"
    fork_result = _api_post(fork_api_url, token)
    
    if not fork_result:
        return None
    
    # Wait a few seconds for fork to complete
    time.sleep(3)
    
    # Return fork URL
    fork_owner = fork_result.get("owner", {}).get("login", user)
    return f"https://github.com/{fork_owner}/{repo_name}.git"


def ensure_forked_repo(repo_url: str, token: str) -> str:
    """
    Ensure we have a fork of the repo (if not owner).
    Returns: repo_url to use (fork if needed, original if owner).
    """
    if not token:
        return repo_url  # No token = use original (will fail on push, but that's expected)
    
    is_owner, existing_fork = check_repo_ownership(repo_url, token)
    
    if is_owner:
        return repo_url  # Own the repo, use original
    
    if existing_fork:
        return existing_fork  # Fork already exists
    
    # Need to create fork
    fork_url = fork_repository(repo_url, token)
    if fork_url:
        return fork_url
    
    # Fork failed, return original (push will fail but we tried)
    return repo_url
