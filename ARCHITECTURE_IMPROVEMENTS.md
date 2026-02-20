# Architecture Improvements — Production-Grade Healing Loop

## API Strategy (Speed + Accuracy)

**Before:** Call all 4–5 APIs per fix → slow  
**After:** Smart provider selection:
- **Simple types** (SYNTAX, INDENTATION, LINTING, IMPORT): 1 provider (fastest first), fallback on failure
- **Complex types** (LOGIC, TYPE_ERROR): 2 providers in parallel, pick best
- **Provider order:** Groq → OpenAI → Gemini → OpenRouter → Ollama
- **Timeout:** 25s per call (configurable via `API_TIMEOUT`)

Result: typically 1 API call per fix (vs 4–5), with similar accuracy.

---

## Summary of Changes

Based on the analysis of regression spikes (1→23 failures), same-line re-fixes, and final pipeline failures, the agent now includes:

---

## 1. Regression Protection

- **Before fixes:** Save git state (`HEAD` commit)
- **After fixes:** Re-scan; if `errors_after > errors_before`, **rollback** to saved state
- **Pre-iteration:** If error count jumps >1.5× from previous iteration, rollback before applying
- **Metric:** `regressions_prevented` shown in dashboard

---

## 2. Severity-Based Fix Ordering

Fixes are applied in this order to reduce cascading errors:

| Priority | Type        | Rationale                          |
|----------|-------------|------------------------------------|
| 1        | SYNTAX      | Must fix first; other checks fail  |
| 2        | INDENTATION | Structural; affects parsing        |
| 3        | IMPORT      | Missing imports break rest of file |
| 4        | TYPE_ERROR  | Type mismatches cause runtime fails|
| 5        | LOGIC       | Test/assertion failures            |
| 6        | LINTING     | Style last; doesn’t block execution|

---

## 3. Convergence Detection

- **Line-level lock:** Don’t fix the same `(file, line)` twice
- **Stuck detection:** If error count is unchanged for 2+ iterations → stop
- **Rollback on regression:** Revert when patches increase error count

---

## 4. Patch Validation (Generate → Validate → Repair → Validate → Commit)

**Architecture:** No snippet editing. Full-file context only.

- **AST validation first:** `ast.parse(code)` before accepting any fix
- **py_compile:** Run `python -m py_compile` on the file after write
- **Self-repair loop:** When syntax fails, send broken code back to LLM: "Your previous fix introduced a syntax error. Fix it without removing existing structure." (up to 3 attempts)
- **autopep8 fallback:** If validation fails, try formatting with autopep8
- **Reject until valid:** Never commit until AST + py_compile pass

---

## 5. Error History (Learn From Mistakes)

- **File:** `agent/error_history.json`
- Records: `error_type`, `error_message`, `fix_applied`, `status`
- Used as **few-shot context** for similar errors
- Reduces repeating the same wrong fix

---

## 6. Ollama Integration (Local Learning)

- **Config:** `OLLAMA_ENABLED=true`, `OLLAMA_BASE_URL=http://localhost:11434/v1`
- Uses local models (e.g. `llama3.2`) with no API key
- Works with error history for few-shot learning
- Run: `ollama run llama3.2` before enabling

---

## 7. Runtime Safety

- **Pytest timeout:** 90 seconds (avoids infinite loops)
- **Jest timeout:** 60 seconds, `--testTimeout=30000` per test
- **py_compile timeout:** 10 seconds

---

## Healing Loop (Pseudocode)

```
for iteration in max_iterations:
    errors_before = scan()
    if errors_before == 0: break (PASSED)

    if errors_now > 1.5 * prev_errors:
        rollback(); continue

    if errors_now == prev_errors for 2 iterations:
        break (convergence_stuck)

    failures = sort_by_severity(scan())
    before_sha = save_state()

    for fail in failures:
        if (file, line) in fixed_lines: skip  # avoid re-fix
        fix = apply_fix(fail)
        if fix applied: fixed_lines.add((file, line))

    errors_after = scan()
    if errors_after > errors_before and applied > 0:
        rollback(before_sha)
        regressions_prevented += 1
        continue

    commit()
```
