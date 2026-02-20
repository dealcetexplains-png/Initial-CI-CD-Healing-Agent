# Multi-runtime image: Node (eslint/jest) + Python (FastAPI + agent + flake8/pyflakes)
FROM node:20-bookworm-slim

# Install Python 3 and pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && ln -sf /usr/bin/pip3 /usr/bin/pip

WORKDIR /app

# Copy project (backend + agent; frontend not needed for API)
COPY backend/ backend/
COPY agent/ agent/
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install global ESLint and Jest so JS/TS repos can be linted and tested
RUN npm install -g eslint jest

# Agent workspace (cloned repos go here)
RUN mkdir -p /app/agent/workspace

# Backend expects repo root on path so "backend" and "agent" resolve
ENV PYTHONPATH=/app
ENV AGENT_WORKSPACE=/app/agent/workspace

# Render sets PORT at runtime; default 8000 for local runs
EXPOSE 8000
CMD ["sh", "-c", "exec python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
