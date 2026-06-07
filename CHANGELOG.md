# Changelog

## v0.1.3 - 2026-06-07

- Protected existing root `CLAUDE.md` files from silent overwrite unless replacement is explicitly approved.
- Resolved project-root defaults through `CLAUDE_PROJECT_DIR` for MCP tools, including `set_effort_level`.
- Kept MCP helper responses structured even when no public status text is provided.
- Updated repository metadata and public version strings for `KimFischer99/CC-Pre-Vibe`.
- Added strict Claude Code plugin validation to CI and development docs.
- Simplified install docs and documented the developer CLI plus `CLAUDE_PROJECT_DIR` behavior.

## v0.1.2 - 2026-06-07

- Shortened skill invocation from `/pre-vibe/pre-vibe-workflow` to `/pre-vibe`.
- Added `pyproject.toml` with Python >=3.11 and mypy/ruff configuration.
- Expanded test coverage from 4 to 109 tests across all core modules.
- Added ruff lint and mypy type-check steps to CI.
- Consolidated privacy and security documentation into single `PRIVACY.md`.
- Updated SKILL.md description with user-facing trigger phrases.

## v0.1.1 - 2026-06-07

- Added explicit handoff enforcement after document generation.
- Added public documentation for installation, quickstart, workflow, troubleshooting, and privacy.
- Added contribution guidance, CI, and focused workflow tests.
- Aligned public package version to v0.1.1.

## v0.1.0

- Initial public Pre-Vibe plugin package.
