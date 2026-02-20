"""Helpers for Python AST-based function edits.

Used to extract and replace a single function in a .py file so that
the LLM only edits the relevant function instead of the whole file.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Optional, Tuple


def load_module(path: Path) -> Tuple[ast.Module, str]:
    """Parse a Python module and return (AST, source_string)."""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    return tree, src


def _get_func_end_line(src: str, func: ast.FunctionDef) -> int:
    """Get last line of function (1-based). Use end_lineno on 3.8+, else indentation."""
    end = getattr(func, "end_lineno", None)
    if end is not None:
        return end
    lines = src.splitlines()
    if func.lineno > len(lines):
        return func.lineno
    # Fallback for Python 3.7: find next line with indent <= def line
    def_indent = len(lines[func.lineno - 1]) - len(lines[func.lineno - 1].lstrip())
    for i in range(func.lineno, len(lines)):
        ln = lines[i]
        if not ln.strip():
            continue
        cur = len(ln) - len(ln.lstrip())
        if cur <= def_indent:
            return i  # 1-based
    return len(lines)


def find_enclosing_function(tree: ast.Module, line: int, src: str = "") -> Optional[ast.FunctionDef]:
    """Find the FunctionDef node that encloses the given 1-based line number."""
    candidates: list[tuple[int, int, ast.FunctionDef]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            end = _get_func_end_line(src, node) if src else getattr(node, "end_lineno", node.lineno)
            if node.lineno <= line <= end:
                candidates.append((node.lineno, end, node))
    if not candidates:
        return None
    # Prefer innermost (smallest range containing line)
    candidates.sort(key=lambda x: (x[1] - x[0], x[0]))
    return candidates[0][2]


def extract_function_source(src: str, func: ast.FunctionDef) -> str:
    """Extract the exact source for a function from the full module source."""
    lines = src.splitlines()
    end = _get_func_end_line(src, func)
    return "\n".join(lines[func.lineno - 1: end])


def replace_function_source(src: str, func: ast.FunctionDef, new_func_src: str) -> str:
    """Replace the function's source in the module with new_func_src."""
    lines = src.splitlines()
    end = _get_func_end_line(src, func)
    before = lines[: func.lineno - 1]
    after = lines[end:]
    new_lines = new_func_src.splitlines()
    # Preserve trailing newline convention
    combined = before + new_lines + after
    return "\n".join(combined)

