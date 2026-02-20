"""Patch validation: AST parse + py_compile before committing (avoid bad patches)."""
import ast
import subprocess
from pathlib import Path


def validate_python_ast(code: str) -> tuple[bool, str]:
    """Reject any fix that fails AST parse. Returns (valid, error_message)."""
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"AST: {e.msg} at line {e.lineno}"


def validate_python_syntax(repo_path: Path, file_path: str) -> tuple[bool, str]:
    """
    Run py_compile on file. Returns (valid, error_message).
    If valid, error_message is empty.
    """
    # Normalize Windows backslashes to Unix forward slashes (cross-platform compatibility)
    normalized_path = file_path.replace("\\", "/")
    full = repo_path / normalized_path
    if not full.exists() or not normalized_path.endswith(".py"):
        return True, ""
    try:
        code = full.read_text(encoding="utf-8")
        ok, err = validate_python_ast(code)
        if not ok:
            return False, err
        # Normalize path string for py_compile (ensure forward slashes)
        normalized_str = str(full).replace("\\", "/")
        r = subprocess.run(
            ["python", "-m", "py_compile", normalized_str],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode != 0:
            error_msg = (r.stderr or r.stdout or "Syntax error")
            # Filter out path-related errors that might be false positives
            if "No such file" in error_msg or "[Errno 2]" in error_msg:
                # If AST passed but py_compile fails with file error, trust AST
                return True, ""
            return False, error_msg
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "Validation timed out"
    except Exception as e:
        return False, str(e)


def validate_changed_files(repo_path: Path, changed_files: list[str]) -> list[tuple[str, str]]:
    """
    Validate all changed Python files. Returns list of (file_path, error_message) for invalid files.
    """
    invalid = []
    for f in changed_files:
        ok, err = validate_python_syntax(repo_path, f)
        if not ok:
            invalid.append((f, err))
    return invalid
