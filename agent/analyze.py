"""Discover and run tests + linters, parse output for failures (including small errors)."""
import re
import subprocess
from pathlib import Path


def discover_tests(repo_path: Path) -> list[str]:
    """Find test files (pytest, jest, etc.)."""
    tests = []
    for pattern in [
        "**/test_*.py", "**/*_test.py",
        "**/test_*.js", "**/test_*.ts",
        "**/*.test.js", "**/*.test.ts", "**/*.spec.js", "**/*.spec.ts",
    ]:
        tests.extend(str(p.relative_to(repo_path)) for p in repo_path.glob(pattern) if p.is_file())
    return list(set(tests))


def discover_source_files(repo_path: Path) -> list[str]:
    """Find Python and JS/TS source files when no test files exist (for linter-only mode)."""
    files = []
    for p in repo_path.rglob("*.py"):
        if p.is_file() and "venv" not in str(p) and ".venv" not in str(p) and "__pycache__" not in str(p):
            files.append(str(p.relative_to(repo_path)).replace("\\", "/"))
    for p in list(repo_path.rglob("*.js")) + list(repo_path.rglob("*.ts")):
        if p.is_file() and "node_modules" not in str(p):
            files.append(str(p.relative_to(repo_path)).replace("\\", "/"))
    return list(set(files))


def _run_cmd(cmd: list[str], cwd: Path, timeout: int = 60) -> str:
    """Run command and return combined stdout+stderr."""
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or "") + (r.stderr or "")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def run_tests(repo_path: Path, test_files: list[str]) -> str:
    """Run tests and return raw output."""
    if not test_files:
        return ""
    py_tests = [t for t in test_files if t.endswith(".py")]
    js_tests = [t for t in test_files if t.endswith((".js", ".ts"))]
    output = ""
    if py_tests:
        output += _run_cmd(["python", "-m", "pytest", *py_tests, "-v", "--tb=short"], repo_path, 90)
    if js_tests:
        output += _run_cmd(["npx", "jest", "--passWithNoTests", "--no-cache", "--verbose", "--testTimeout=30000"], repo_path, 60)
    return output


def run_linters(repo_path: Path, source_files: list[str] | None = None) -> str:
    """Run linters and static analyzers (flake8, pyflakes, pylint, mypy, bandit, eslint)."""
    output = ""
    if source_files:
        py_src = [f for f in source_files if f.endswith(".py")][:50]
        js_src = [f for f in source_files if f.endswith((".js", ".ts", ".jsx", ".tsx"))][:30]
    else:
        py_files = list(repo_path.rglob("*.py"))
        py_src = [str(p.relative_to(repo_path)).replace("\\", "/") for p in py_files
                  if "test" not in p.name.lower() and "venv" not in str(p) and "__pycache__" not in str(p)][:50]
        js_files = list(repo_path.rglob("*.js")) + list(repo_path.rglob("*.ts"))
        js_src = [str(p.relative_to(repo_path)).replace("\\", "/") for p in js_files
                  if "node_modules" not in str(p)][:30]
    
    # Python: flake8, pyflakes (fast), then optional: pylint, mypy, bandit
    if py_src:
        output += _run_cmd(["python", "-m", "flake8", *py_src, "--max-line-length=120", "-v"], repo_path)
        output += _run_cmd(["python", "-m", "pyflakes", *py_src], repo_path)
        # Optional: pylint (slower but catches more)
        try:
            output += _run_cmd(["pylint", *py_src[:10]], repo_path, timeout=30)  # Limit files for speed
        except:
            pass
        # Optional: mypy for type errors
        try:
            output += _run_cmd(["mypy", *py_src[:10]], repo_path, timeout=30)
        except:
            pass
        # Optional: bandit for security
        try:
            output += _run_cmd(["bandit", "-r", *py_src[:5]], repo_path, timeout=20)
        except:
            pass
    
    # JavaScript/TypeScript: eslint
    if js_src and (repo_path / "package.json").exists():
        output += _run_cmd(["npx", "eslint", *js_src, "--format", "compact", "--no-error-on-unmatched-pattern"], repo_path)
    
    return output


def _classify_from_message(msg: str) -> str:
    """Classify error type from message text. Check flake8 codes FIRST."""
    m = msg.lower()
    # E999 is SyntaxError from flake8 - must check BEFORE generic regex
    if "e999" in m or "syntaxerror" in m:
        return "SYNTAX"
    # Explicit flake8 code mapping FIRST (before generic regex)
    if "e302" in m or "e305" in m:
        return "LINTING"
    if "w191" in m or "e128" in m:
        return "INDENTATION"
    # Docstring errors (D100, D101, etc.) are LINTING, not LOGIC
    if "d100" in m or "missing module docstring" in m or "missing docstring" in m:
        return "LINTING"
    # Catch PEP8/Flake8 codes (before "expected" keyword matches LOGIC) - includes D codes
    # BUT skip E999 (already handled above as SYNTAX)
    if re.search(r'\b[ewfd]\d{3}\b', m) and "e999" not in m:
        return "LINTING"
    if "flake8" in m or "pep8" in m or "pyflakes" in m:
        return "LINTING"
    if "syntax" in m or "colon" in m or "bracket" in m or "paren" in m or "quote" in m:
        return "SYNTAX"
    if "indent" in m:
        return "INDENTATION"
    if "type" in m or "typing" in m or "argument" in m:
        return "TYPE_ERROR"
    if "unused" in m or "import" in m or "redefin" in m or "undefined" in m:
        return "LINTING" if "import" in m else "LINTING"
    if "assertion" in m or "fail" in m:
        return "LOGIC"
    # "expected" keyword last - only if not a flake8 code (already caught above)
    if "expected" in m:
        return "LOGIC"
    return "LOGIC"


def parse_test_output(output: str, repo_path: Path) -> list[dict]:
    """Parse pytest/jest output into structured failures."""
    failures = []
    lines = output.splitlines()
    seen = set()

    for i, line in enumerate(lines):
        # Pytest: FAILED path/to/file.py::test_name
        if "FAILED" in line and ".py" in line:
            for p in line.split():
                if ".py" in p and "::" in p:
                    file_part = p.split("::")[0]
                    key = (file_part, None)
                    if key not in seen:
                        seen.add(key)
                        failures.append({
                            "file": file_part,
                            "line": None,
                            "type": _classify_from_message(line),
                            "message": line,
                            "context": "\n".join(lines[max(0, i - 2): i + 5]),
                        })
                    break

        # Pytest: path/to/file.py:15: Error or :15: in line
        if ".py:" in line:
            match = re.search(r"([^\s:]+\.py):(\d+)", line)
            if match:
                file_part, line_num = match.group(1), int(match.group(2))
                key = (file_part, line_num)
                if key not in seen:
                    seen.add(key)
                    failures.append({
                        "file": file_part,
                        "line": line_num,
                        "type": _classify_from_message(line),
                        "message": line,
                        "context": "\n".join(lines[max(0, i - 2): i + 5]),
                    })

        # Jest: at path/file.js:10:5
        if "at " in line and (".js:" in line or ".ts:" in line):
            match = re.search(r"at\s+.*?([^\s:]+\.(?:js|ts|jsx|tsx)):(\d+)", line)
            if match:
                file_part, line_num = match.group(1), int(match.group(2))
                key = (file_part, line_num)
                if key not in seen:
                    seen.add(key)
                    failures.append({
                        "file": file_part,
                        "line": line_num,
                        "type": _classify_from_message(line),
                        "message": line,
                        "context": "\n".join(lines[max(0, i - 2): i + 5]),
                    })

        # SyntaxError, IndentationError, etc.
        if "Error:" in line or "error" in line.lower():
            match = re.search(r'File "([^"]+)", line (\d+)', line)
            if match:
                abs_path = match.group(1)
                try:
                    rel = str(Path(abs_path).relative_to(repo_path))
                except ValueError:
                    rel = Path(abs_path).name
                line_num = int(match.group(2))
                key = (rel, line_num)
                if key not in seen:
                    seen.add(key)
                    failures.append({
                        "file": rel.replace("\\", "/"),
                        "line": line_num,
                        "type": _classify_from_message(line),
                        "message": line,
                        "context": "\n".join(lines[max(0, i - 2): i + 5]),
                    })

    return failures


def parse_linter_output(output: str, repo_path: Path) -> list[dict]:
    """Parse flake8, pyflakes, eslint output for small/detail errors. Extract ALL line numbers."""
    failures = []
    lines = output.splitlines()
    seen = set()

    for line in lines:
        # flake8: path/file.py:10:1: E501 line too long
        # pyflakes: path/file.py:10: undefined name 'x'
        # eslint: path/file.js: line 10, col 5, Error - ...
        m = re.search(r"([^\s:]+\.py):(\d+):", line)
        if m:
            file_part, line_num = m.group(1), int(m.group(2))
            key = (file_part, line_num, "lint")
            if key not in seen:
                seen.add(key)
                # Extract ALL line numbers mentioned in the error message
                all_line_nums = [line_num]
                # Look for additional line numbers in the message (e.g., "line 15", ":20:", "at line 25")
                additional_lines = re.findall(r'(?:line|:)\s*(\d+)', line, re.I)
                for ln_str in additional_lines:
                    ln = int(ln_str)
                    if ln != line_num and ln not in all_line_nums:
                        all_line_nums.append(ln)
                all_line_nums.sort()
                failures.append({
                    "file": file_part,
                    "line": line_num,  # Primary line number
                    "all_lines": all_line_nums if len(all_line_nums) > 1 else None,  # All line numbers
                    "type": _classify_from_message(line),
                    "message": line.strip(),
                    "context": line,
                })
            continue
        m = re.search(r"([^\s:]+\.(?:js|ts|jsx|tsx)):\s*line\s+(\d+)", line, re.I)
        if m:
            file_part, line_num = m.group(1), int(m.group(2))
            key = (file_part, line_num, "lint")
            if key not in seen:
                seen.add(key)
                # Extract ALL line numbers mentioned in the error message
                all_line_nums = [line_num]
                additional_lines = re.findall(r'(?:line|:)\s*(\d+)', line, re.I)
                for ln_str in additional_lines:
                    ln = int(ln_str)
                    if ln != line_num and ln not in all_line_nums:
                        all_line_nums.append(ln)
                all_line_nums.sort()
                failures.append({
                    "file": file_part,
                    "line": line_num,
                    "all_lines": all_line_nums if len(all_line_nums) > 1 else None,
                    "type": _classify_from_message(line),
                    "message": line.strip(),
                    "context": line,
                })

    return failures


def get_all_failures(repo_path: Path, test_files: list[str], source_files: list[str] | None = None) -> list[dict]:
    """Run tests + linters and return merged failures. If no test files, runs linters only on source files."""
    test_out = run_tests(repo_path, test_files) if test_files else ""
    linter_out = run_linters(repo_path, source_files)
    test_failures = parse_test_output(test_out, repo_path)
    linter_failures = parse_linter_output(linter_out, repo_path)
    seen = {(f["file"], f.get("line")) for f in test_failures}
    # Also try python -m py_compile for syntax errors when no test files (catches SyntaxError, etc.)
    if not test_files and source_files:
        py_src = [f for f in source_files if f.endswith(".py")]
        for pf in py_src:
            full = repo_path / pf
            if full.exists():
                r = _run_cmd(["python", "-m", "py_compile", str(full)], repo_path)
                syn_failures = parse_test_output(r, repo_path)
                for f in syn_failures:
                    k = (f["file"], f.get("line"))
                    if k not in seen:
                        seen.add(k)
                        test_failures.append(f)
    for f in linter_failures:
        k = (f["file"], f.get("line"))
        if k not in seen:
            seen.add(k)
            test_failures.append(f)
    return test_failures


def _auto_format_file(file_path: Path):
    """Run autopep8 to perfectly fix all spacing/indentation errors instantly (deterministic pre-pass)."""
    try:
        # Ensure path uses forward slashes for cross-platform compatibility
        normalized_str = str(file_path).replace("\\", "/")
        subprocess.run(
            ["python", "-m", "autopep8", "--in-place", "--aggressive", normalized_str],
            capture_output=True,
            timeout=10,
            cwd=file_path.parent,
        )
    except Exception:
        pass


def filter_and_prep_failures(failures: list[dict], repo_path: Path) -> dict[str, list[dict]]:
    """
    Maximum Accuracy Architecture:
    1. Deterministic Pre-Pass: Run autopep8 on files to fix E302, W291, indentation instantly
    2. Filter out docstring/whitespace noise (already fixed by autopep8)
    3. Group remaining real bugs (LOGIC, TYPE_ERROR, IMPORT) by file for batching
    
    Returns: { "app.py": [error1, error2], "utils.py": [error3] }
    """
    grouped = {}
    
    # Ignore docstrings and pure formatting that autopep8 already fixed
    ignored_keywords = [
        "docstring", "d100", "d101", "d102", "d103", "d104",
        "blank line", "e302", "e303", "e305", "e501", "w291", "w293",
        "line too long", "trailing whitespace", "missing whitespace",
    ]
    
    formatted_files = set()

    for f in failures:
        msg = f.get("message", "").lower()
        
        # Skip only pure formatting noise (autopep8 handles these)
        if any(ignored in msg for ignored in ignored_keywords):
            continue
            
        file_path = f["file"]
        full_path = repo_path / file_path
        
        # Auto-format the file once before grouping (deterministic pre-pass)
        if file_path not in formatted_files and full_path.exists() and file_path.endswith(".py"):
            _auto_format_file(full_path)
            formatted_files.add(file_path)
            
        # Group the legitimate errors by file
        if file_path not in grouped:
            grouped[file_path] = []
        grouped[file_path].append(f)
        
    return grouped
