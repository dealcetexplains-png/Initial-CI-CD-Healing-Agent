"""Rollback mechanism: save state before fixes, revert on regression."""
from pathlib import Path

import git


def save_state(repo_path: Path) -> str | None:
    """Save current git state (HEAD commit hash). Returns commit hash or None."""
    try:
        repo = git.Repo(repo_path)
        return repo.head.commit.hexsha
    except Exception:
        return None


def rollback_to(repo_path: Path, commit_sha: str) -> bool:
    """Reset repo to given commit (hard). Returns True on success."""
    try:
        repo = git.Repo(repo_path)
        repo.git.reset("--hard", commit_sha)
        return True
    except Exception:
        return False


def stash_changes(repo_path: Path) -> bool:
    """Stash uncommitted changes. Returns True on success."""
    try:
        repo = git.Repo(repo_path)
        if repo.is_dirty():
            repo.git.stash("push", "-m", "ai-agent-before-fix")
        return True
    except Exception:
        return False


def restore_stash(repo_path: Path) -> bool:
    """Restore stashed changes. Returns True on success."""
    try:
        repo = git.Repo(repo_path)
        repo.git.stash("pop")
        return True
    except Exception:
        return False
