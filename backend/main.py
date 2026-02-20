"""FastAPI server for the CI/CD Healing Agent."""
import asyncio
import json
import sys
import time
from pathlib import Path

# Ensure project root is on path (for agent imports)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.runner import run_healing_agent

app = FastAPI(title="CI/CD Healing Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    repo_url: str
    team_name: str
    team_leader: str


class RunResponse(BaseModel):
    task_id: str
    message: str
    status: str = "started"


# In-memory store for run results (use Redis/DB in production)
run_results: dict = {}


def format_branch_name(team_name: str, team_leader: str) -> str:
    """Format branch: TEAM_NAME_LEADER_NAME_AI_Fix. Must be different from main/master."""
    import re
    team = re.sub(r"[^\w\-]", "_", team_name.strip().upper().replace(" ", "_"))
    leader = re.sub(r"[^\w\-]", "_", team_leader.strip().upper().replace(" ", "_"))
    branch = f"{team}_{leader}_AI_Fix"
    # Ensure NEVER equals main/master
    if branch.lower() in ("main", "master", "trunk") or not branch:
        branch = f"ai_fix_{branch or 'branch'}"
    return branch[:100]


@app.post("/api/run", response_model=RunResponse)
async def trigger_agent(request: RunRequest, background_tasks: BackgroundTasks):
    """Trigger the autonomous healing agent."""
    task_id = f"{int(time.time() * 1000)}"
    
    branch_name = format_branch_name(request.team_name, request.team_leader)
    
    async def run_task():
        start = time.time()
        try:
            result = await asyncio.to_thread(
                run_healing_agent,
                repo_url=request.repo_url,
                team_name=request.team_name,
                team_leader=request.team_leader,
                branch_name=branch_name,
            )
            result["total_time_seconds"] = round(time.time() - start, 2)
            run_results[task_id] = result
        except Exception as e:
            run_results[task_id] = {
                "error": str(e),
                "status": "failed",
                "total_time_seconds": round(time.time() - start, 2),
            }

    background_tasks.add_task(run_task)
    
    return RunResponse(
        task_id=task_id,
        message="Agent started. Poll /api/result/{task_id} for status.",
        status="started",
    )


@app.get("/api/result/{task_id}")
async def get_result(task_id: str):
    """Get run result by task_id."""
    if task_id not in run_results:
        return {"status": "running", "message": "Agent still processing"}
    return run_results[task_id]


@app.get("/api/health")
async def health():
    """Health check."""
    return {"status": "ok"}


def save_results_json(result: dict, path: Path):
    """Save results.json for submission."""
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
