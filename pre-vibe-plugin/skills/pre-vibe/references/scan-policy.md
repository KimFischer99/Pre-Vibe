# Safe Scan Policy

## Default Allowlist

- `README.md`, `README.*`
- `AGENTS.md`
- `CLAUDE.md`
- `.claude/rules/`
- `docs/`
- `package.json`, lockfiles, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`
- PRD/spec/design documents named by the task or visible at project root
- Source and test directory names as a tree summary
- Specific source files only when the task or project evidence points to them

## Default Denylist

- `.env`, `.env.*`
- private keys and certificates
- token caches
- local database dumps
- production logs
- credential files
- personal data exports

If environment information is needed, ask first. Read variable names or safe metadata
only; never read secret values by default.

## Evidence Rule

Final artifacts may say a file, setting, or tool exists only after it was actually
observed. If something was not inspected, record it as an assumption or unknown.
