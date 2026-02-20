"""Intelligent LLM model selection based on error type and capabilities.

Maps error types to best-suited models for optimal accuracy and speed.
"""
from typing import Optional


# Model capabilities by error type
# Format: {error_type: {provider: [model1, model2, ...]} }
# Models listed in order of preference (best first)
MODEL_SELECTION = {
    "LOGIC": {
        "OpenRouter": [
            "anthropic/claude-3.5-sonnet",  # Best reasoning
            "openai/gpt-4o",  # Strong code understanding
            "openai/gpt-4-turbo",
            "google/gemini-pro-1.5",
            "meta-llama/llama-3.1-70b-instruct",
            "openai/gpt-4o-mini",  # Fallback
        ],
        "OpenAI": [
            "gpt-4o",  # Best for complex logic
            "gpt-4-turbo",
            "gpt-4o-mini",  # Faster fallback
        ],
        "Groq": [
            "llama-3.3-70b-versatile",  # Good reasoning
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768",
        ],
        "Gemini": [
            "gemini-2.0-flash",  # Fast + capable (correct model name)
            "gemini-1.5-flash",  # Fallback
            "gemini-1.5-pro",
        ],
        "Ollama": [
            "llama3.2",  # Local fallback
            "codellama",
        ],
    },
    "TYPE_ERROR": {
        "OpenRouter": [
            "openai/gpt-4o",  # Strong type understanding
            "anthropic/claude-3.5-sonnet",
            "google/gemini-pro-1.5",
            "openai/gpt-4o-mini",
        ],
        "OpenAI": [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4o-mini",
        ],
        "Groq": [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
        ],
        "Gemini": [
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ],
        "Ollama": [
            "codellama",  # Code-focused
            "llama3.2",
        ],
    },
    "SYNTAX": {
        "OpenRouter": [
            "openai/gpt-4o",  # Precise syntax fixes
            "anthropic/claude-3.5-sonnet",
            "openai/gpt-4o-mini",  # Fast for simple syntax
            "google/gemini-2.0-flash",
        ],
        "OpenAI": [
            "gpt-4o",
            "gpt-4o-mini",  # Fast enough for syntax
        ],
        "Groq": [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
        ],
        "Gemini": [
            "gemini-2.0-flash",  # Fast
            "gemini-2.0-flash",
        ],
        "Ollama": [
            "codellama",  # Code-focused
            "llama3.2",
        ],
    },
    "IMPORT": {
        "OpenRouter": [
            "openai/gpt-4o-mini",  # Simple fixes, fast is fine
            "openai/gpt-4o",
            "google/gemini-2.0-flash",
        ],
        "OpenAI": [
            "gpt-4o-mini",  # Fast + accurate enough
            "gpt-4o",
        ],
        "Groq": [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
        ],
        "Gemini": [
            "gemini-2.0-flash",  # Fast
            "gemini-1.5-flash",  # Fallback
        ],
        "Ollama": [
            "llama3.2",
        ],
    },
    "INDENTATION": {
        "OpenRouter": [
            "openai/gpt-4o-mini",  # Simple, use fast model
            "google/gemini-2.0-flash",
        ],
        "OpenAI": [
            "gpt-4o-mini",
        ],
        "Groq": [
            "llama-3.1-70b-versatile",
        ],
        "Gemini": [
            "gemini-2.0-flash",
            "gemini-1.5-flash",
        ],
        "Ollama": [
            "llama3.2",
        ],
    },
    "LINTING": {
        # Note: LINTING should use tools (autopep8), but if LLM needed:
        "OpenRouter": [
            "openai/gpt-4o-mini",  # Fast for style fixes
            "google/gemini-2.0-flash",
        ],
        "OpenAI": [
            "gpt-4o-mini",
        ],
        "Groq": [
            "llama-3.1-70b-versatile",
        ],
        "Gemini": [
            "gemini-2.0-flash",
            "gemini-1.5-flash",
        ],
        "Ollama": [
            "llama3.2",
        ],
    },
}


def get_best_model_for_error(
    provider: str,
    error_type: str,
    available_providers: list[str],
) -> Optional[str]:
    """
    Select best model for error type and provider.
    Returns model name or None if not available.
    """
    error_type = error_type.upper()
    
    # Default fallback models if error type not in mapping
    default_models = {
        "OpenRouter": "openai/gpt-4o-mini",
        "OpenAI": "gpt-4o-mini",
        "Groq": "llama-3.3-70b-versatile",
        "Gemini": "gemini-2.0-flash",
        "Ollama": "llama3.2",
    }
    
    if provider not in available_providers:
        return None
    
    # Get model list for this error type and provider
    models = MODEL_SELECTION.get(error_type, {}).get(provider)
    if not models:
        return default_models.get(provider)
    
    # Return first model (best for this error type)
    return models[0]


def get_all_models_for_error(
    provider: str,
    error_type: str,
    available_providers: list[str],
) -> list[str]:
    """
    Get all models for error type and provider (best first).
    Returns list of model names for fallback.
    """
    error_type = error_type.upper()
    
    # Default fallback models if error type not in mapping
    default_models = {
        "OpenRouter": ["openai/gpt-4o-mini"],
        "OpenAI": ["gpt-4o-mini"],
        "Groq": ["llama-3.3-70b-versatile"],
        "Gemini": ["gemini-2.0-flash", "gemini-1.5-flash"],
        "Ollama": ["llama3.2"],
    }
    
    if provider not in available_providers:
        return []
    
    # Get model list for this error type and provider
    models = MODEL_SELECTION.get(error_type, {}).get(provider)
    if not models:
        return default_models.get(provider, [])
    
    return models


def get_provider_order_for_error(error_type: str, available_providers: list[str]) -> list[str]:
    """
    Get optimal provider order for error type.
    Returns list of providers ordered by best fit.
    """
    error_type = error_type.upper()
    
    # Provider priority by error type
    priority_map = {
        "LOGIC": ["OpenAI", "OpenRouter", "Groq", "Gemini", "Ollama"],  # Need best reasoning
        "TYPE_ERROR": ["OpenAI", "OpenRouter", "Gemini", "Groq", "Ollama"],  # Type understanding
        "SYNTAX": ["OpenAI", "OpenRouter", "Groq", "Gemini", "Ollama"],  # Precise fixes
        "IMPORT": ["OpenRouter", "OpenAI", "Groq", "Gemini", "Ollama"],  # Fast is fine
        "INDENTATION": ["OpenRouter", "Groq", "Gemini", "OpenAI", "Ollama"],  # Fast models
        "LINTING": ["OpenRouter", "Groq", "Gemini", "OpenAI", "Ollama"],  # Should use tools, but fast if needed
    }
    
    order = priority_map.get(error_type, ["OpenRouter", "OpenAI", "Groq", "Gemini", "Ollama"])
    
    # Filter to only available providers
    return [p for p in order if p in available_providers]


def should_use_ensemble(error_type: str) -> bool:
    """Determine if error type benefits from ensemble (multiple models)."""
    # Complex errors benefit from ensemble
    return error_type.upper() in ("LOGIC", "TYPE_ERROR")


# Heavy models for escalation when small models fail
HEAVY_MODELS = {
    "OpenRouter": "anthropic/claude-3.5-sonnet",
    "OpenAI": "gpt-4o",
    "Groq": "llama-3.3-70b-versatile",
    "Gemini": "gemini-1.5-pro",
    "Ollama": "codellama",
}


def get_heavy_model_for_escalation(provider: str, available_providers: list[str]) -> Optional[str]:
    """Get the best/heavy model for escalation when small models fail."""
    if provider not in available_providers:
        return None
    return HEAVY_MODELS.get(provider)
