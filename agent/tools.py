"""Automated code fixing tools integration.

Supports: autopep8, black, prettier, eslint, rubocop, pylint, mypy, bandit
Tool selection based on error type and language.
"""
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def _run_tool(cmd: list[str], cwd: Path, input_text: str | None = None, timeout: int = 30) -> Tuple[bool, str]:
    """Run a tool command. Returns (success, output)."""
    try:
        r = subprocess.run(
            cmd,
            cwd=cwd,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return r.returncode == 0, (r.stdout or "") + (r.stderr or "")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "Tool not found or timed out"


def _check_tool_available(tool: str) -> bool:
    """Check if a tool is installed."""
    try:
        subprocess.run(
            [tool, "--version"],
            capture_output=True,
            timeout=5,
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _check_python_module(module: str) -> bool:
    """Check if a Python module is available."""
    try:
        subprocess.run(
            ["python", "-m", module, "--version"],
            capture_output=True,
            timeout=5,
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# Python formatters
def format_with_autopep8(file_path: Path, repo_path: Path) -> Tuple[bool, str]:
    """Format Python file with autopep8."""
    if not _check_tool_available("python"):
        return False, "Python not found"
    # Normalize path for cross-platform compatibility
    normalized_path = str(file_path).replace("\\", "/")
    ok, out = _run_tool(
        ["python", "-m", "autopep8", "--in-place", normalized_path],
        cwd=repo_path,
    )
    return ok, out


def format_with_black(file_path: Path, repo_path: Path) -> Tuple[bool, str]:
    """Format Python file with black."""
    if not _check_tool_available("black"):
        return False, "black not installed"
    ok, out = _run_tool(
        ["black", str(file_path)],
        cwd=repo_path,
    )
    return ok, out


# JavaScript/TypeScript formatters
def format_with_prettier(file_path: Path, repo_path: Path) -> Tuple[bool, str]:
    """Format JS/TS file with prettier."""
    if not _check_tool_available("npx"):
        return False, "npx not found"
    ok, out = _run_tool(
        ["npx", "--yes", "prettier", "--write", str(file_path)],
        cwd=repo_path,
    )
    return ok, out


def fix_with_eslint(file_path: Path, repo_path: Path) -> Tuple[bool, str]:
    """Auto-fix JS/TS file with eslint."""
    if not _check_tool_available("npx"):
        return False, "npx not found"
    ok, out = _run_tool(
        ["npx", "--yes", "eslint", "--fix", str(file_path)],
        cwd=repo_path,
    )
    return ok, out


# Ruby formatter
def format_with_rubocop(file_path: Path, repo_path: Path) -> Tuple[bool, str]:
    """Format Ruby file with rubocop."""
    if not _check_tool_available("rubocop"):
        return False, "rubocop not installed"
    ok, out = _run_tool(
        ["rubocop", "-A", str(file_path)],
        cwd=repo_path,
    )
    return ok, out


# Python static analyzers
def analyze_with_pylint(file_path: Path, repo_path: Path) -> Tuple[bool, str]:
    """Run pylint on Python file."""
    if not _check_tool_available("pylint"):
        return False, "pylint not installed"
    ok, out = _run_tool(
        ["pylint", str(file_path)],
        cwd=repo_path,
    )
    return ok, out


def analyze_with_mypy(file_path: Path, repo_path: Path) -> Tuple[bool, str]:
    """Run mypy type checker on Python file."""
    if not _check_tool_available("mypy"):
        return False, "mypy not installed"
    ok, out = _run_tool(
        ["mypy", str(file_path)],
        cwd=repo_path,
    )
    return ok, out


def analyze_with_bandit(file_path: Path, repo_path: Path) -> Tuple[bool, str]:
    """Run bandit security analyzer on Python file."""
    if not _check_tool_available("bandit"):
        return False, "bandit not installed"
    ok, out = _run_tool(
        ["bandit", "-r", str(file_path)],
        cwd=repo_path,
    )
    return ok, out


def auto_fix_file(
    file_path: Path,
    repo_path: Path,
    error_type: str,
    language: str | None = None,
) -> Tuple[bool, str, str]:
    """
    Auto-fix file using appropriate tool based on error type and language.
    Returns: (success, tool_name, output)
    """
    if language is None:
        if file_path.suffix == ".py":
            language = "python"
        elif file_path.suffix in (".js", ".jsx", ".ts", ".tsx"):
            language = "javascript"
        elif file_path.suffix == ".rb":
            language = "ruby"
        else:
            return False, "unknown", "Unsupported file type"

    # LINTING / INDENTATION errors → use formatters
    if error_type in ("LINTING", "INDENTATION"):
        if language == "python":
            # Try autopep8 first (more compatible), then black
            ok, out = format_with_autopep8(file_path, repo_path)
            if ok:
                return True, "autopep8", out
            ok, out = format_with_black(file_path, repo_path)
            if ok:
                return True, "black", out
        elif language == "javascript":
            # Try eslint --fix first, then prettier
            ok, out = fix_with_eslint(file_path, repo_path)
            if ok:
                return True, "eslint", out
            ok, out = format_with_prettier(file_path, repo_path)
            if ok:
                return True, "prettier", out
        elif language == "ruby":
            ok, out = format_with_rubocop(file_path, repo_path)
            if ok:
                return True, "rubocop", out

    # TYPE_ERROR → use type checkers (they can't auto-fix, but we can report)
    if error_type == "TYPE_ERROR" and language == "python":
        ok, out = analyze_with_mypy(file_path, repo_path)
        # mypy doesn't auto-fix, but we can use its output for LLM context
        return False, "mypy", out  # Return False so LLM handles it

    return False, "none", "No auto-fix tool available"


def get_available_tools(language: str) -> list[str]:
    """Return list of available tools for a language."""
    tools = []
    if language == "python":
        if _check_python_module("autopep8"):
            tools.append("autopep8")
        if _check_tool_available("black"):
            tools.append("black")
        if _check_tool_available("pylint"):
            tools.append("pylint")
        if _check_tool_available("mypy"):
            tools.append("mypy")
        if _check_tool_available("bandit"):
            tools.append("bandit")
    elif language == "javascript":
        if _check_tool_available("npx"):
            # Assume prettier/eslint available via npx (will auto-install)
            tools.append("prettier")
            tools.append("eslint")
    elif language == "ruby":
        if _check_tool_available("rubocop"):
            tools.append("rubocop")
    return tools
