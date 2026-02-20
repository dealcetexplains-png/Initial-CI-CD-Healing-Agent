"""Severity-based fix ordering. Fix SYNTAX first, then IMPORT, TYPE_ERROR, etc."""
# Order: 1=highest priority, 7=lowest
SEVERITY_ORDER = {
    "SYNTAX": 1,
    "INDENTATION": 2,
    "IMPORT": 3,
    "TYPE_ERROR": 4,
    "LOGIC": 5,
    "LINTING": 6,
}


def get_priority(err_type: str) -> int:
    """Return priority (lower = fix first)."""
    return SEVERITY_ORDER.get(err_type.upper(), 5)


def sort_failures_by_severity(failures: list[dict]) -> list[dict]:
    """Sort failures: SYNTAX first, then INDENTATION, IMPORT, TYPE_ERROR, LOGIC, LINTING."""
    return sorted(failures, key=lambda f: (get_priority(f.get("type", "LOGIC")), f.get("file", ""), f.get("line") or 0))
