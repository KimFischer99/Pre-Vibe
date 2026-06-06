# Safe Scan Policy

The project execution index is mandatory before blocking questions. Keep it shallow for
`mini`, but still inspect safe root files, project guidance, and top-level structure.

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

## Codex Component Index

Before asking questions, inspect:

- Global and project AGENTS guidance.
- Installed plugins and plugin cache entries.
- Installed skills from Codex and user skill directories.
- Slash prompt command files under the Codex prompts directory.
- Marketplace presence for the current plugin.

SPEC component recommendations must be tied to this evidence. If a useful component is
missing, recommend search-backed confirmation or installation rather than pretending it
is available.
