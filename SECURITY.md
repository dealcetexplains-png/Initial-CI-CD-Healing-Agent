# Security Notice

## API Keys

- **Never** commit API keys to version control.
- Use `.env` for local development (copy from `.env.example`).
- Add `.env` to `.gitignore` (already done).
- If you accidentally exposed keys, **rotate them immediately** in the respective provider dashboards.

## Recommended Setup

1. Copy `.env.example` → `.env`
2. Paste your keys into `.env` only
3. Delete any `apis.txt` or similar files with keys before pushing
