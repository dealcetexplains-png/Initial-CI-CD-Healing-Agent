# Detailed Setup Guide — CI/CD Healing Agent

This guide walks you through setting up the project step-by-step on Windows, macOS, or Linux.

---

## Prerequisites

### 1. Node.js 18+

- **Check:** Run `node -v` in terminal.
- **Install:** Download from [nodejs.org](https://nodejs.org) or use `nvm` / `fnm`.

### 2. Python 3.10+

- **Check:** Run `python --version` or `python3 --version`.
- **Install:** Download from [python.org](https://www.python.org/downloads/).

### 3. Git

- **Check:** Run `git --version`.
- **Install:** [git-scm.com](https://git-scm.com/).

---

## Step 1: Get the Project

If you have the project folder:

```bash
cd "e:\rift ci,cd"
```

If cloning from GitHub:

```bash
git clone https://github.com/YOUR_ORG/rift-cicd-healing-agent.git
cd rift-cicd-healing-agent
```

---

## Step 2: Environment Variables (API Keys)

The agent uses **all configured AI APIs** and combines their outputs for better results. Add as many keys as you have.

### Create `.env`

1. Copy the example file:

   - **Windows:** `copy .env.example .env`
   - **macOS/Linux:** `cp .env.example .env`

2. Edit `.env` and add your API keys:

```env
# OpenRouter (recommended - multi-model)
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY

# OpenAI
OPENAI_API_KEY=sk-proj-YOUR_KEY

# Google Gemini
GOOGLE_API_KEY=AIzaSyYOUR_KEY

# Groq
GROQ_API_KEY=gsk_YOUR_KEY

# GitHub CI (optional - poll GitHub Actions after push)
GITHUB_TOKEN=ghp_YOUR_TOKEN

# Optional
AGENT_RETRY_LIMIT=5
AGENT_WORKSPACE=./agent/workspace
GITHUB_CI_TIMEOUT=300
```

### API key sources

| API      | Where to get a key                           |
|----------|----------------------------------------------|
| OpenRouter | [openrouter.ai/keys](https://openrouter.ai/keys) |
| OpenAI   | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| Gemini   | [ai.google.dev](https://ai.google.dev/) (Google AI Studio) |
| Groq     | [console.groq.com](https://console.groq.com/) |

At least one key is required. More keys = stronger ensemble (all responses are combined for the final fix).

**GitHub Actions integration:** Add `GITHUB_TOKEN` (classic or fine-grained with `actions: read`) to poll workflow runs after each push. When set, the agent waits for GitHub Actions and uses that result; if CI passes, it stops early.

---

## Step 2.5: Optional Tools (Recommended)

The agent uses automated tools for faster, more reliable fixes. Install optional tools:

### Python Tools (Recommended)
```bash
pip install -r backend/requirements-optional.txt
```

This installs:
- **autopep8** - Auto-formats Python (fixes LINTING errors instantly)
- **black** - Code formatter (alternative to autopep8)
- **pylint** - Advanced linting
- **mypy** - Type checking
- **bandit** - Security scanning

**Impact:** LINTING errors are fixed in 0.1-2 seconds (vs 5-30s with LLM). 100% success rate.

### JavaScript/TypeScript Tools
No installation needed! The agent uses `npx` to auto-install:
- **prettier** - Code formatter
- **eslint** - Linter with auto-fix

### Ruby Tools
```bash
gem install rubocop
```

See `TOOLS.md` for full documentation.

---

## Step 3: Backend Setup

### Option A: Virtual environment (recommended)

**Windows (PowerShell or CMD):**

```bash
cd "e:\rift ci,cd"

# Create venv
python -m venv backend\venv

# Activate
backend\venv\Scripts\activate

# Install
pip install -r backend\requirements.txt

# Optional: add Gemini support
pip install google-generativeai

# Run
python backend\main.py
```

**macOS / Linux:**

```bash
cd /path/to/rift-ci-cd

python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
pip install google-generativeai   # optional, for Gemini
python backend/main.py
```

### Option B: Global Python

```bash
pip install -r backend/requirements.txt
python backend/main.py
```

### Verify backend

- Open: http://localhost:8000/health  
- Expected: `{"status":"ok"}`

---

## Step 4: Frontend Setup

In a **new terminal** (keep the backend running):

**Windows:**

```bash
cd "e:\rift ci,cd\frontend"

npm install
npm run dev
```

**macOS / Linux:**

```bash
cd /path/to/rift-ci-cd/frontend
npm install
npm run dev
```

### Verify frontend

- Open: http://localhost:5173  
- You should see the dashboard.

---

## Step 5: Run the Full App

### Option 1: Manual (two terminals)

**Terminal 1 — Backend:**

```bash
cd "e:\rift ci,cd"
backend\venv\Scripts\activate    # Windows
pip install -r backend\requirements.txt
python backend\main.py
```

**Terminal 2 — Frontend:**

```bash
cd "e:\rift ci,cd\frontend"
npm install
npm run dev
```

### Option 2: Start script (Windows)

```bash
cd "e:\rift ci,cd"
start.bat
```

This opens two windows: one for backend, one for frontend.

---

## How the Multi-API Ensemble Works

1. For each detected failure, the agent calls **every configured API** (OpenRouter, OpenAI, Gemini, Groq).
2. Each API returns a suggested fix.
3. The ensemble logic:
   - Compares outputs and chooses the most consistent fix (majority).
   - If no clear majority, picks the most complete one.
4. The chosen fix is applied and committed.

Configured APIs are shown in the dashboard under **AI Providers** in the Fixes table.

---

## Troubleshooting

### Backend won't start

- **"No module named 'agent'"** → Run from project root: `python backend/main.py` (not from inside `backend/`).
- **"No API key configured"** → Add at least one key to `.env`.

### Frontend shows "invalid response"

- Ensure the backend is running on port 8000.
- Open http://localhost:8000/health to confirm.

### Agent fails to clone repo

- Check internet connection and that the GitHub URL is correct and public.
- For private repos: configure a `GITHUB_TOKEN` and update the clone logic.

### Gemini errors

- Make sure `GOOGLE_API_KEY` is the API key from [Google AI Studio](https://aistudio.google.com/), not a service account key.

---

## Project structure (quick reference)

```
rift-ci-cd/
├── frontend/           # React (Vite)
│   └── src/
├── backend/            # FastAPI
│   ├── main.py
│   └── config.py
├── agent/              # Healing logic
│   ├── ai_providers.py # OpenRouter, OpenAI, Gemini, Groq
│   ├── ensemble.py     # Combines API outputs
│   ├── fix.py          # Apply fixes
│   ├── clone.py
│   ├── analyze.py
│   └── commit.py
├── .env
├── .env.example
└── SETUP.md
```
