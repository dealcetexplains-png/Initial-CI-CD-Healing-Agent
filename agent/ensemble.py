"""
Intelligent LLM selection: choose best model per error type for optimal accuracy.
- LOGIC/TYPE_ERROR: Best reasoning models (GPT-4o, Claude, Gemini Pro)
- SYNTAX: Precise models (GPT-4o, Claude)
- IMPORT/INDENTATION/LINTING: Fast models (GPT-4o-mini, Gemini Flash)
- Ensemble for complex types: Multiple models in parallel, pick best
"""
from concurrent.futures import ThreadPoolExecutor, as_completed

from agent.ai_providers import (
    call_openrouter,
    call_openai,
    call_gemini,
    call_groq,
    call_ollama,
    get_available_providers,
)
from agent.model_selector import (
    get_all_models_for_error,
    get_best_model_for_error,
    get_heavy_model_for_escalation,
    get_provider_order_for_error,
    should_use_ensemble,
)


def _call_provider(name: str, system: str, user: str, model: str | None = None) -> tuple[str | None, str]:
    """Call single provider with optional model override. Returns (content, provider_name)."""
    if name == "OpenRouter":
        return call_openrouter(system, user, model or "openai/gpt-4o-mini")
    if name == "OpenAI":
        return call_openai(system, user, model or "gpt-4o-mini")
    if name == "Gemini":
        return call_gemini(system, user, model or "gemini-2.0-flash")
    if name == "Groq":
        return call_groq(system, user, model or "llama-3.3-70b-versatile")
    if name == "Ollama":
        return call_ollama(system, user, model or "llama3.2")
    return None, name


def _is_valid_content(content: str | None, min_len: int = 15) -> bool:
    """Check if response is usable."""
    if not content or not content.strip():
        return False
    if len(content.strip()) < min_len:
        return False
    return True


def _pick_best(candidates: list[tuple[str, str]]) -> tuple[str | None, list[str]]:
    """Pick longest valid response. Returns (content, [winning_provider])."""
    valid = [(c, p) for c, p in candidates if _is_valid_content(c)]
    if not valid:
        return None, []
    best = max(valid, key=lambda x: len(x[0]))
    return best[0], [best[1]]


def generate_fix_ensemble(
    system_prompt: str,
    user_prompt: str,
    few_shot_context: str = "",
    bug_type: str = "LOGIC",
    use_ensemble_for_complex: bool = True,
    escalate_to_heavy: bool = False,
) -> tuple[str | None, list[str], dict]:
    """
    Intelligent LLM selection based on error type:
    - LOGIC/TYPE_ERROR: Best reasoning models (GPT-4o, Claude) + ensemble
    - SYNTAX: Precise models (GPT-4o, Claude)
    - IMPORT/INDENTATION/LINTING: Fast models (GPT-4o-mini, Gemini Flash)
    - escalate_to_heavy: Use heavy models (GPT-4o, Claude 3.5) when small models failed
    
    Returns: (final_content, providers_used, raw_results)
    """
    raw_results: dict[str, str | None] = {}
    providers = get_available_providers()
    if not providers:
        return None, [], {}

    # Get optimal provider order - use ALL available providers
    order = get_provider_order_for_error(bug_type, providers)
    if not order:
        return None, [], {}

    if few_shot_context:
        user_prompt = f"Learn from these past fixes (avoid repeating same mistakes):\n{few_shot_context}\n\n---\n\n{user_prompt}"

    # Model selection: heavy models when escalating (small LLMs failed)
    def _get_models(provider: str) -> list[str]:
        """Get list of models to try (best first)."""
        if escalate_to_heavy:
            heavy = get_heavy_model_for_escalation(provider, providers)
            if heavy:
                return [heavy]
        # Get all models for this error type (best first)
        all_models = get_all_models_for_error(provider, bug_type, providers)
        if all_models:
            return all_models
        # Fallback to single best model
        best = get_best_model_for_error(provider, bug_type, providers)
        return [best] if best else []

    # Determine if ensemble is beneficial - use ALL providers when ensemble
    use_ensemble = use_ensemble_for_complex and (should_use_ensemble(bug_type) or escalate_to_heavy) and len(order) >= 2
    providers_to_try = order  # Use ALL providers, not just top 3

    if use_ensemble:
        # Call ALL providers in parallel with optimal models
        candidates: list[tuple[str, str, str]] = []  # (content, provider, model)
        tried_providers = set()
        
        with ThreadPoolExecutor(max_workers=min(len(providers_to_try), 6)) as ex:
            futures = {}
            for provider in providers_to_try:
                models = _get_models(provider)
                if models:
                    # Try first model (best)
                    model = models[0]
                    futures[ex.submit(_call_provider, provider, system_prompt, user_prompt, model)] = (provider, model, models)
            
            for fut in as_completed(futures, timeout=120):
                provider, model, all_models = futures[fut]
                tried_providers.add(provider)
                try:
                    content, _ = fut.result()
                except Exception as e:
                    raw_results[f"{provider}({model})"] = f"ERROR: {repr(e)}"
                    # Try fallback models for this provider
                    for fallback_model in all_models[1:]:
                        try:
                            fallback_content, _ = _call_provider(provider, system_prompt, user_prompt, fallback_model)
                            raw_results[f"{provider}({fallback_model})"] = fallback_content
                            if _is_valid_content(fallback_content):
                                candidates.append((fallback_content, provider, fallback_model))
                                break
                        except Exception as e2:
                            raw_results[f"{provider}({fallback_model})"] = f"ERROR: {repr(e2)}"
                    continue
                raw_results[f"{provider}({model})"] = content
                if _is_valid_content(content):
                    candidates.append((content, provider, model))
        
        if candidates:
            # Pick best (longest usually = most complete)
            best = max(candidates, key=lambda x: len(x[0]))
            return best[0], [best[1]], raw_results
        
        # Fallback: try remaining providers with all their models
        for provider in order:
            if provider in tried_providers:
                continue
            models = _get_models(provider)
            if not models:
                continue
            for model in models:
                try:
                    content, _ = _call_provider(provider, system_prompt, user_prompt, model)
                except Exception as e:
                    raw_results[f"{provider}({model})"] = f"ERROR: {repr(e)}"
                    continue
                raw_results[f"{provider}({model})"] = content
                if _is_valid_content(content):
                    return content, [provider], raw_results
    else:
        # Simple errors: try each provider until one succeeds (with fallback models)
        for provider in order:
            models = _get_models(provider)
            if not models:
                continue
            for model in models:
                try:
                    content, _ = _call_provider(provider, system_prompt, user_prompt, model)
                except Exception as e:
                    raw_results[f"{provider}({model})"] = f"ERROR: {repr(e)}"
                    continue  # Try next model
                raw_results[f"{provider}({model})"] = content
                if _is_valid_content(content):
                    return content, [provider], raw_results

    return None, list(providers), raw_results
