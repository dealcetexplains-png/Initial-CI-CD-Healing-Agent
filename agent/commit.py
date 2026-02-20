"""Commit and push fixes to new branch."""
import re
from pathlib import Path

import git


def _sanitize_branch_name(name: str) -> str:
    """Sanitize branch name for Git. Only alphanumeric, hyphens, underscores."""
    sanitized = re.sub(r"[^\w\-]", "_", name)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    return sanitized[:100] if sanitized else "ai_fix_branch"


def commit_and_push(
    repo_path: Path,
    branch_name: str,
    commit_message: str,
) -> bool:
    """
    Ensure we're on user branch, commit changes, and push to origin.
    Branch is created in clone_repo - here we just commit and push.
    Returns True on success.
    """
    try:
        repo = git.Repo(repo_path)
        safe_branch = _sanitize_branch_name(branch_name)
        main_branches = {"main", "master", "trunk"}

        # Ensure branch name is different from main
        if safe_branch.lower() in main_branches:
            safe_branch = f"ai_fix_{safe_branch}"

        # Checkout branch (should already exist from clone)
        if safe_branch in [b.name for b in repo.branches]:
            repo.git.checkout(safe_branch)
        else:
            repo.git.checkout("-b", safe_branch)

        repo.git.add(A=True)
        if repo.is_dirty():
            repo.index.commit(commit_message)
            try:
                origin = repo.remotes.origin
                origin.push(safe_branch, force=True)
            except Exception as e:
                # Log push failure - don't silently fail
                error_msg = str(e)
                print(f"[ERROR] Push failed for branch {safe_branch}: {error_msg}")
                # Return False so caller knows push failed
                return False
        return True
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Commit failed: {error_msg}")
        return False
