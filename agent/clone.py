"""Clone repository, create user branch, and checkout (robust, avoids path collisions)."""
from pathlib import Path
import re

import git

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent.github_fork import ensure_forked_repo
from backend.config import GITHUB_TOKEN


def _get_unique_dest(workspace: Path, base_name: str) -> Path:
    """
    Return a destination path that does not already exist.
    If 'base_name' exists, append a numeric suffix.
    """
    dest = workspace / base_name
    if not dest.exists():
        return dest
    i = 1
    while True:
        alt = workspace / f"{base_name}_{i}"
        if not alt.exists():
            return alt
        i += 1


def _sanitize_branch_name(name: str) -> str:
    """Sanitize branch name: only alphanumeric, hyphens, underscores. Max 100 chars."""
    # Replace spaces and invalid chars with underscores
    sanitized = re.sub(r"[^\w\-]", "_", name)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    return sanitized[:100] if sanitized else "ai_fix_branch"


def ensure_branch_exists(repo_path: Path, branch_name: str) -> bool:
    """
    Create and checkout the user's branch immediately after clone.
    Ensures branch is different from main/master. Returns True on success.
    """
    try:
        repo = git.Repo(repo_path)
        main_branches = {"main", "master", "trunk"}

        # Sanitize branch name
        safe_branch = _sanitize_branch_name(branch_name)

        # Ensure branch name is different from main
        if safe_branch.lower() in main_branches or not safe_branch:
            safe_branch = f"ai_fix_{safe_branch or 'branch'}"

        # Create and checkout new branch
        if safe_branch in [b.name for b in repo.branches]:
            repo.git.checkout(safe_branch)
        else:
            repo.git.checkout("-b", safe_branch)

        return True
    except Exception:
        return False


def clone_repo(repo_url: str, workspace: Path, branch_name: str | None = None) -> Path | None:
    """
    Clone repo into workspace with auto-fork for non-owned repos.
    - Checks ownership via GitHub API
    - If not owner: forks repo automatically, then clones fork
    - If owner: clones original repo
    - Never reuses an existing non-empty folder (avoids corrupted .git or permission issues).
    - Always chooses a fresh folder name if the base one already exists.
    - If branch_name provided, creates and checks out that branch (different from main).
    """
    # Ensure we have a fork if needed (for non-owned repos)
    final_repo_url = ensure_forked_repo(repo_url, GITHUB_TOKEN)
    
    # Extract repo name for folder
    name = final_repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    workspace.mkdir(parents=True, exist_ok=True)

    dest = _get_unique_dest(workspace, name)

    # Fresh clone into a non-existing directory
    git.Repo.clone_from(final_repo_url, dest)

    # Create and checkout user branch immediately (must be different from main)
    if branch_name:
        ensure_branch_exists(dest, branch_name)

    return dest
