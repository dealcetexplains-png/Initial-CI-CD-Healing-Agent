# Autonomous CI/CD Healing Agent

**RIFT 2026 • Multi-city Hackathon • AIML Track**

An autonomous DevOps agent that detects, fixes, and verifies code issues in GitHub repositories. Features a production-ready React dashboard for monitoring and control.

---

## 🚀 Quick Start

> **Full setup instructions:** See [SETUP.md](./SETUP.md) for step-by-step setup, API key configuration, and troubleshooting.

### Prerequisites
- Node.js 18+
- Python 3.10+
- Git
- Docker (recommended for sandboxed execution)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd rift-cicd-healing-agent

# Backend (Python)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Optional: pip install google-generativeai  # for Gemini

# Frontend (React)
cd ../frontend
npm install

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Setup

1. Copy `.env.example` to `.env`
2. Add your API keys (OpenRouter, OpenAI, Gemini, or Groq)
3. Configure `AGENT_RETRY_LIMIT` (default: 5)

### Usage

```bash
# Terminal 1 - Start backend
cd backend && python main.py

# Terminal 2 - Start frontend
cd frontend && npm run dev

# Open http://localhost:5173
```

---

## 📁 Project Structure

```
rift-cicd-healing-agent/
├── frontend/           # React dashboard (Vite)
├── backend/            # FastAPI server + Agent orchestration
├── agent/              # Autonomous healing logic
│   ├── clone.py        # Clone repo
│   ├── analyze.py      # Discover & run tests
│   ├── fix.py          # AI-powered fixes
│   ├── commit.py       # Commit & push
│   └── runner.py       # Main pipeline
├── architecture-diagram.md
├── CURSOR_PROMPT.md    # Prompts for Cursor AI
└── README.md
```

---

## 🎯 Supported Bug Types

| Type | Description |
|------|-------------|
| LINTING | Unused imports, style violations |
| SYNTAX | Missing colons, brackets, quotes |
| LOGIC | Incorrect logic, wrong conditions |
| TYPE_ERROR | Type mismatches |
| IMPORT | Missing or incorrect imports |
| INDENTATION | Wrong indentation (Python) |

---

## 📋 Branch Naming

Format: `TEAM_NAME_LEADER_NAME_AI_Fix`

- All uppercase
- Spaces → underscores
- Example: `RIFT_ORGANISERS_SAIYAM_KUMAR_AI_Fix`

---

## 🔧 Tech Stack

- **Frontend:** React, Vite, Context API
- **Backend:** Python FastAPI
- **Agent:** Multi-step orchestration with **ensemble AI** (uses all configured APIs)
- **AI:** OpenRouter, OpenAI, Gemini, Groq — all responses are combined for better fixes

---

## ⚠️ Known Limitations

- Python and JavaScript/TypeScript projects only
- Requires repo to have discoverable test files
- GitHub token needed for private repos

---

## 📄 License

MIT

---

**Team:** [Your Team Name]  
**Deployment URL:** [Add after deployment]  
**LinkedIn Demo:** [Add after recording]
