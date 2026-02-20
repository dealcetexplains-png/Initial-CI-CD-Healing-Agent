"""Configuration for the CI/CD Healing Agent."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load from project root or backend folder
root = Path(__file__).resolve().parent.parent
load_dotenv(root / ".env")
load_dotenv()

# API Keys (use one - OpenRouter is OpenAI-compatible)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"

# GitHub CI (optional - poll Actions after push)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_CI_ENABLED = bool(GITHUB_TOKEN)
GITHUB_CI_TIMEOUT = int(os.getenv("GITHUB_CI_TIMEOUT", "300"))

# Agent config - MAXIMUM POWER MODE
AGENT_RETRY_LIMIT = int(os.getenv("AGENT_RETRY_LIMIT", "15"))  # Maximum iterations to fix all errors
USE_ENSEMBLE_FOR_COMPLEX = os.getenv("USE_ENSEMBLE_FOR_COMPLEX", "true").lower() == "true"
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))  # Longer timeout for heavy models
MAX_FIXES_PER_ITERATION = int(os.getenv("MAX_FIXES_PER_ITERATION", "20"))  # Fix more errors per iteration
AGENT_WORKSPACE = Path(os.getenv("AGENT_WORKSPACE", "./agent/workspace"))

# Base URL for OpenRouter (OpenAI-compatible)
OPENROUTER_BASE = "https://openrouter.ai/api/v1"
