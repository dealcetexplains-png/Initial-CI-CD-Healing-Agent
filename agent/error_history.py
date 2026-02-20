"""
Error history: store error→fix pairs to avoid repeating mistakes.
Used as few-shot examples when generating fixes (learns from past errors).
"""
import json
from pathlib import Path

_HISTORY_PATH = Path(__file__).resolve().parent.parent / "agent" / "error_history.json"
_MAX_ENTRIES = 100


def _load() -> list[dict]:
    if _HISTORY_PATH.exists():
        try:
            return json.loads(_HISTORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def _save(history: list[dict]) -> None:
    _HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    _HISTORY_PATH.write_text(json.dumps(history[-_MAX_ENTRIES:], indent=2), encoding="utf-8")


def add(error_type: str, error_message: str, fix_applied: str, status: str = "Fixed") -> None:
    """Record an error and its fix (or failure)."""
    history = _load()
    history.append({
        "type": error_type,
        "message": error_message[:500],
        "fix": fix_applied[:1000] if fix_applied else "",
        "status": status,
    })
    _save(history)


def get_few_shot_examples(error_type: str, limit: int = 3) -> str:
    """Get recent successful fixes for similar error type as few-shot examples."""
    history = _load()
    relevant = [h for h in history if h.get("type") == error_type and h.get("status") == "Fixed"][-limit:]
    if not relevant:
        return ""
    lines = []
    for h in relevant:
        lines.append(f"Past fix for {h['type']}:")
        lines.append(f"  Error: {h.get('message', '')[:200]}...")
        lines.append(f"  Fix excerpt: {h.get('fix', '')[:300]}...")
    return "\n".join(lines) if lines else ""
