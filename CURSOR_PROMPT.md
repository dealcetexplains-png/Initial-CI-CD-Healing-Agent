# Cursor AI Prompt for CI/CD Healing Agent

Use this prompt in Cursor to generate or extend components:

---

## Prompt: Generate Agent Component

```
I'm building an Autonomous CI/CD Healing Agent for RIFT 2026. The agent must:

1. Clone a GitHub repo
2. Discover test files (pytest, jest)
3. Run tests and parse failures
4. Use AI (OpenRouter/OpenAI) to generate fixes for: LINTING, SYNTAX, LOGIC, TYPE_ERROR, IMPORT, INDENTATION
5. Apply fixes and commit with [AI-AGENT] prefix
6. Push to branch TEAM_NAME_LEADER_NAME_AI_Fix (uppercase, underscores)
7. Iterate until tests pass or retry limit (5)
8. Output results.json with: repo_url, branch_name, fixes[], timeline[], score

Output format for fixes: "TYPE error in path line N → Fix: description"
Bug types: LINTING, SYNTAX, LOGIC, TYPE_ERROR, IMPORT, INDENTATION
```

---

## Prompt: Improve React Dashboard

```
Add/improve the React dashboard for the CI/CD Healing Agent. Requirements:

1. Input: repo URL, team name, team leader, Run Agent button, loading state
2. Run Summary: repo URL, team, branch, failures, fixes, CI status (PASSED/FAILED), time
3. Score: base 100, speed bonus +10 if <5min, efficiency penalty -2 per commit over 20
4. Fixes Table: File, Bug Type, Line, Commit Message, Status (Fixed/Failed), color-coded
5. Timeline: each CI run, pass/fail badge, iterations used
6. Responsive, production-ready, dark theme
```

---

## Prompt: Add LangGraph / Multi-Agent

```
Refactor the CI/CD healing agent to use LangGraph (or CrewAI/AutoGen) for multi-agent architecture:
- Analyzer agent: discovers tests, runs them, parses output
- Fixer agent: classifies bug type, generates fix
- Orchestrator: coordinates flow, retry logic
- Use state graph with nodes for clone, analyze, fix, commit
```
