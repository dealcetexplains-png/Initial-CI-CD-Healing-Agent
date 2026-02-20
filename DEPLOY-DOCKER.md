# Deploy Backend with Docker on Render (Python + Node)

This setup lets the hosted agent run **Python** (flake8, pyflakes, pytest) and **JavaScript/TypeScript** (eslint, jest) so repos like `buggy-website` report real failures and fixes.

## 1. Prerequisites

- Code pushed to GitHub (including `Dockerfile`, `requirements.txt`, `.dockerignore`).

## 2. Render: New Web Service (Docker)

1. Go to [Render](https://render.com) → **New +** → **Web Service**.
2. Connect your repo (e.g. `Initial-CI-CD-Healing-Agent`).
3. **Environment**: select **Docker** (not Python).
4. **Branch**: `main`.
5. **Name**: e.g. `cicd-healing-agent`.
6. **Region**: choose one.
7. **Plan**: Free.

Render will use the repo’s `Dockerfile`; no build/start command needed.

## 3. Environment variables (optional)

In the Render service → **Environment** add any of:

- `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `GROQ_API_KEY` (for AI fixes).
- `GITHUB_TOKEN` (if you use GitHub Actions CI checks).
- `AGENT_WORKSPACE` is set in the Dockerfile; override only if needed.

## 4. Deploy

Click **Create Web Service**. Wait for the first build (a few minutes).  
Your API URL will be like: `https://cicd-healing-agent.onrender.com`.

## 5. Point frontend to the new backend

- **Vercel**: set `VITE_API_URL` = `https://<your-render-service>.onrender.com/api`.
- Or in `frontend/src/context/AppContext.jsx`, update the production fallback URL to the new Render URL.

Redeploy the frontend after changing the API URL.

## 6. Test

- Open your Vercel app and run the agent on `https://github.com/dealcetexplains-png/buggy-website.git`.
- You should see **Failures > 0** and **Fixes Applied** (and real error lines) once the Docker backend is in use.

## Local Docker test (optional)

```bash
docker build -t healing-agent .
docker run -p 8000:8000 healing-agent
```

Then open `http://localhost:8000/docs` and run the frontend with `VITE_API_URL=http://localhost:8000/api`.
