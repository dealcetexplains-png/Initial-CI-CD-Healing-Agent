"""
AI provider adapters for OpenRouter, OpenAI, Gemini, and Groq.
Each returns (content, provider_name) or (None, provider_name) on failure.
"""
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE,
    OPENAI_API_KEY,
    GOOGLE_API_KEY,
    GROQ_API_KEY,
    OLLAMA_BASE_URL,
    OLLAMA_ENABLED,
    API_TIMEOUT,
)


def _clean_content(text: str | None) -> str:
    """Remove markdown code blocks and normalize."""
    if not text or not text.strip():
        return ""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def call_openrouter(system: str, user: str, model: str = "openai/gpt-4o-mini") -> tuple[str | None, str]:
    """OpenRouter (multi-model)."""
    if not OPENROUTER_API_KEY:
        return None, "OpenRouter"
    from openai import OpenAI
    client = OpenAI(base_url=OPENROUTER_BASE, api_key=OPENROUTER_API_KEY)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.1,
        timeout=API_TIMEOUT,
    )
    content = (resp.choices[0].message.content or "").strip()
    return _clean_content(content), "OpenRouter"


def call_openai(system: str, user: str, model: str = "gpt-4o-mini") -> tuple[str | None, str]:
    """OpenAI."""
    if not OPENAI_API_KEY:
        return None, "OpenAI"
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.1,
        timeout=API_TIMEOUT,
    )
    content = (resp.choices[0].message.content or "").strip()
    return _clean_content(content), "OpenAI"


def call_gemini(system: str, user: str, model: str = "gemini-2.0-flash") -> tuple[str | None, str]:
    """Google Gemini. Requires: pip install google-generativeai"""
    if not GOOGLE_API_KEY:
        return None, "Gemini"
    import google.generativeai as genai  # pip install google-generativeai
    genai.configure(api_key=GOOGLE_API_KEY)
    mdl = genai.GenerativeModel(model)
    full_prompt = f"{system}\n\n{user}"
    resp = mdl.generate_content(full_prompt)
    content = (resp.text or "").strip()
    return _clean_content(content), "Gemini"


def call_groq(system: str, user: str, model: str = "llama-3.3-70b-versatile") -> tuple[str | None, str]:
    """Groq (OpenAI-compatible)."""
    if not GROQ_API_KEY:
        return None, "Groq"
    from openai import OpenAI
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY,
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.1,
        timeout=API_TIMEOUT,
    )
    content = (resp.choices[0].message.content or "").strip()
    return _clean_content(content), "Groq"


def call_ollama(system: str, user: str, model: str = "llama3.2") -> tuple[str | None, str]:
    """Ollama (local). Learns from errors - use with error_history for few-shot. No API key needed."""
    if not OLLAMA_ENABLED:
        return None, "Ollama"
    from openai import OpenAI
    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.1,
        timeout=API_TIMEOUT,
    )
    content = (resp.choices[0].message.content or "").strip()
    return _clean_content(content), "Ollama"


def get_available_providers() -> list[str]:
    """Return list of provider names that have API keys configured."""
    providers = []
    if OPENROUTER_API_KEY:
        providers.append("OpenRouter")
    if OPENAI_API_KEY:
        providers.append("OpenAI")
    if GOOGLE_API_KEY:
        providers.append("Gemini")
    if GROQ_API_KEY:
        providers.append("Groq")
    if OLLAMA_ENABLED:
        providers.append("Ollama")
    return providers
