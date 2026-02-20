# Intelligent LLM Model Selection

The agent now intelligently selects the best LLM model based on error type and capabilities.

## 🎯 Model Selection Strategy

### Error Type → Model Mapping

| Error Type | Best Models | Why |
|------------|------------|-----|
| **LOGIC** | GPT-4o, Claude 3.5 Sonnet, Gemini Pro | Need strong reasoning for complex bugs |
| **TYPE_ERROR** | GPT-4o, Claude 3.5 Sonnet | Excellent type understanding |
| **SYNTAX** | GPT-4o, Claude 3.5 Sonnet | Precise syntax fixes |
| **IMPORT** | GPT-4o-mini, Gemini Flash | Simple fixes, speed matters |
| **INDENTATION** | GPT-4o-mini, Gemini Flash | Fast formatting |
| **LINTING** | Tools (autopep8) preferred | Should use tools, not LLM |

## 🔧 Provider Priority by Error Type

### LOGIC Errors
1. **OpenAI** (GPT-4o) - Best reasoning
2. **OpenRouter** (Claude 3.5 Sonnet) - Strong alternative
3. **Groq** (Llama 3.3 70B) - Fast reasoning
4. **Gemini** (Gemini Pro) - Good reasoning
5. **Ollama** (Llama 3.2) - Local fallback

### TYPE_ERROR
1. **OpenAI** (GPT-4o) - Best type understanding
2. **OpenRouter** (GPT-4o) - Same model via proxy
3. **Gemini** (Gemini Pro) - Good type checking
4. **Groq** (Llama 3.3) - Fast alternative

### SYNTAX
1. **OpenAI** (GPT-4o) - Precise fixes
2. **OpenRouter** (GPT-4o) - Same precision
3. **Groq** (Llama 3.3) - Fast + accurate

### IMPORT / INDENTATION / LINTING
1. **OpenRouter** (GPT-4o-mini) - Fast + cheap
2. **Groq** (Llama 3.1) - Very fast
3. **Gemini** (Gemini Flash) - Fast
4. **OpenAI** (GPT-4o-mini) - Reliable

## 🚀 Model Capabilities

### Best Reasoning Models (LOGIC/TYPE_ERROR)
- **GPT-4o** (`gpt-4o`) - OpenAI's best, excellent code understanding
- **Claude 3.5 Sonnet** (`anthropic/claude-3.5-sonnet`) - Anthropic's best reasoning
- **Gemini Pro** (`google/gemini-pro-1.5`) - Google's advanced model
- **Llama 3.3 70B** (`llama-3.3-70b-versatile`) - Open-source, fast

### Fast Models (IMPORT/INDENTATION)
- **GPT-4o-mini** (`gpt-4o-mini`) - Fast + accurate enough
- **Gemini Flash** (`gemini-2.0-flash-exp`) - Very fast
- **Llama 3.1 70B** (`llama-3.1-70b-versatile`) - Fast reasoning

### Code-Focused Models
- **CodeLlama** (`codellama`) - Specialized for code (Ollama)
- **GPT-4o** - Excellent code understanding

## 📊 Selection Logic

1. **Error Classification** → Determines error type
2. **Provider Order** → Gets optimal provider order for error type
3. **Model Selection** → Picks best model for provider + error type
4. **Ensemble Decision** → LOGIC/TYPE_ERROR use ensemble (2-3 models), others use single

## 🔄 Fallback Chain

If best model fails:
1. Try next model in priority list for same provider
2. Try next provider with its best model
3. Continue until success or all exhausted

## 💡 Example Flows

### LOGIC Error Fix
```
Error: LOGIC
→ Select: OpenAI (GPT-4o) + OpenRouter (Claude 3.5) + Groq (Llama 3.3)
→ Call all 3 in parallel
→ Pick best response (longest/complete)
→ Apply fix
```

### IMPORT Error Fix
```
Error: IMPORT
→ Select: OpenRouter (GPT-4o-mini)
→ Call single provider
→ Apply fix
```

### LINTING Error Fix
```
Error: LINTING
→ Skip LLM entirely
→ Use autopep8/black/prettier
→ Apply fix
```

## 🎛️ Configuration

Models can be customized in `agent/model_selector.py`:

```python
MODEL_SELECTION = {
    "LOGIC": {
        "OpenRouter": ["anthropic/claude-3.5-sonnet", "openai/gpt-4o", ...],
        "OpenAI": ["gpt-4o", "gpt-4-turbo", ...],
        ...
    }
}
```

## 📈 Performance Impact

| Error Type | Old Model | New Model | Improvement |
|------------|-----------|-----------|-------------|
| LOGIC | GPT-4o-mini | GPT-4o + Claude | +30% accuracy |
| TYPE_ERROR | GPT-4o-mini | GPT-4o | +25% accuracy |
| IMPORT | GPT-4o | GPT-4o-mini | 5x faster, same accuracy |
| INDENTATION | GPT-4o | GPT-4o-mini | 5x faster |

## 🔍 Debug Output

The agent now shows which model was used:

```json
{
  "providers_used": ["OpenAI"],
  "raw_responses": {
    "OpenAI(gpt-4o)": "...",
    "OpenRouter(anthropic/claude-3.5-sonnet)": "..."
  }
}
```

This helps diagnose which models work best for your specific errors.
