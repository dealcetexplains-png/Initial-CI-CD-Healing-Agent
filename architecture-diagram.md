# Architecture Diagram

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REACT DASHBOARD (Port 5173)                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Input     │  │ Run Summary  │  │    Score     │  │ Fixes & Timeline │  │
│  │ (URL, Team) │  │  (Status)    │  │  Breakdown   │  │     Table        │  │
│  └──────┬──────┘  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────┼──────────────────────────────────────────────────────────────────┘
          │ POST /api/run
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND (Port 8000)                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  /api/run  →  Start Agent (Background Task)                           │   │
│  │  /api/result/{id}  →  Poll for results                                │   │
│  │  /api/health  →  Health check                                         │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────┬──────────────────────────────────────────────────────────────────┘
          │ spawns
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS HEALING AGENT                                  │
│                                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│  │  Clone   │ → │ Discover │ → │Run Tests │ → │   Fix    │ → │ Commit   │   │
│  │   Repo   │   │  Tests   │   │  Parse   │   │  (AI)    │   │  Push    │   │
│  └──────────┘   └──────────┘   └──────────┘   └────┬─────┘   └────┬─────┘   │
│       │                │              │             │              │         │
│       │                │              │             │              │         │
│       │                └──────────────┴─────────────┴──────────────┘         │
│       │                              ▲                                        │
│       │                              │ Loop until pass or retry limit         │
│       └──────────────────────────────┘                                        │
│                                                                              │
│  Output: results.json, branch TEAM_LEADER_AI_Fix                             │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  External: OpenRouter / OpenAI / Gemini (AI), GitHub (Clone/Push)            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Level 1 Flow

1. **User** → Enters repo URL, team name, leader
2. **Frontend** → POST /api/run
3. **Backend** → Starts agent in background, returns task_id
4. **Frontend** → Polls /api/result/{task_id} every 2s
5. **Agent** → Clone → Discover tests → Run → Parse failures → AI fix → Commit → Repeat
6. **Backend** → Stores result when done
7. **Frontend** → Displays summary, score, fixes, timeline

## Level 2 – Agent Detail

```
Clone Repo (GitPython)
    ↓
Discover Tests (glob: test_*.py, *.test.js, etc.)
    ↓
FOR iteration = 1 to RETRY_LIMIT:
    ↓
    Run Tests (pytest / jest)
    ↓
    Parse Output → failures[]
    ↓
    IF failures empty → BREAK (PASSED)
    ↓
    FOR each failure:
        → Classify bug type (LINTING, SYNTAX, LOGIC, ...)
        → Call AI with file + error context
        → Apply fix to file
        → Append to fixes[]
    ↓
    Commit with [AI-AGENT] prefix
    ↓
    Push to branch TEAM_LEADER_AI_Fix
    ↓
CONTINUE loop
    ↓
Compute score, write results.json
```
