"""GitHub Actions CI integration: wait for workflow runs after push."""
import re
import time
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import urllib.request
    import urllib.error
    import urllib.parse
    import json as _json
except ImportError:
    urllib = None
    _json = None


def _parse_repo_url(repo_url: str) -> tuple[str, str] | None:
    """Extract owner/repo from GitHub URL. Returns (owner, repo) or None."""
    m = re.match(
        r"https?://(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",
        repo_url.strip().rstrip("/"),
    )
    if m:
        return m.group(1), m.group(2)
    return None


def _api_get(url: str, token: str, timeout: int = 15) -> dict | None:
    """GET GitHub API and return JSON or None."""
    if not urllib or not _json:
        return None
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return _json.loads(r.read().decode())
    except Exception:
        return None


def wait_for_workflow_runs(
    repo_url: str,
    branch: str,
    token: str,
    timeout_seconds: int = 300,
    poll_interval: int = 10,
) -> dict:
    """
    Poll GitHub Actions for workflow runs on the given branch.
    Returns: {
        "status": "success" | "failure" | "timeout" | "no_workflows" | "error",
        "runs": [...],
        "conclusion": "success" | "failure" | ...,
        "message": str,
    }
    """
    parsed = _parse_repo_url(repo_url)
    if not parsed:
        return {"status": "error", "message": "Invalid GitHub URL", "runs": []}
    owner, repo = parsed

    url = (
        f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
        f"?branch={urllib.parse.quote(branch, safe='')}"
        f"&per_page=10"
        f"&event=push"
    )

    start = time.monotonic()
    last_runs: list = []
    # Workflows take a few seconds to appear after push
    time.sleep(5)

    while (time.monotonic() - start) < timeout_seconds:
        data = _api_get(url, token, timeout=15)
        if not data or "workflow_runs" not in data:
            time.sleep(poll_interval)
            continue

        runs = data.get("workflow_runs", [])
        runs = [r for r in runs if r.get("head_branch") == branch]
        last_runs = runs

        if not runs:
            time.sleep(poll_interval)
            continue

        all_completed = True
        any_failure = False
        for r in runs:
            status = r.get("status", "")
            conclusion = r.get("conclusion") or ""
            if status in ("queued", "in_progress", "pending", "waiting", "requested"):
                all_completed = False
                break
            if conclusion in ("failure", "cancelled", "timed_out"):
                any_failure = True

        if all_completed:
            return {
                "status": "failure" if any_failure else "success",
                "runs": runs,
                "conclusion": "failure" if any_failure else "success",
                "message": f"{len(runs)} workflow(s) completed",
            }

        time.sleep(poll_interval)

    return {
        "status": "timeout" if last_runs else "no_workflows",
        "runs": last_runs,
        "conclusion": None,
        "message": "Timeout waiting for workflows" if last_runs else "No workflow runs found",
    }
