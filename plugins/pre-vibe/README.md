# Pre-Vibe Plugin Package

This directory is the distributable Codex plugin package for Pre-Vibe v0.1.1.

Pre-Vibe is backed by a local stdio MCP server and plugin-scoped workflow guidance. Users enable it from the Codex plugin picker, then start with a rough task or starter prompt.

## Components

- `.codex-plugin/plugin.json`: Codex plugin manifest.
- `.mcp.json`: bundled MCP server registration.
- `skills/pre-vibe-workflow/SKILL.md`: workflow guidance for Codex orchestration.
- `scripts/pre_vibe.py`: compatibility facade and CLI.
- `scripts/mcp_server.py`: stdio MCP server.
- `scripts/pv_*.py`: focused workflow modules.
- `LICENSE`: package license.

## Runtime Behavior

The MCP server exposes tools that prepare project starts, inspect safe local context, read Codex guidance, manage effort settings, request native question UI, and write Codex-authored starting documents.

Tool results use short user-visible status text such as "正在构建项目初始文档。". Detailed workflow state is returned as structured content for Codex.

`write_project_starting_documents` is not the final workflow step. After it writes files, Codex must request user approval for `FIRST_PROMPT.md`; after approval, Codex must read and inject `FIRST_PROMPT.md` as the execution contract.

## Documents Written

- `PRE_VIBE_SPEC.md`
- `AGENTS.md` or `PROJECT_AGENTS.md`
- `FIRST_PROMPT.md`
- `PROJECT_INDEX.md` for architect effort

## Validation

From the repository root:

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/pre-vibe
python3 -m py_compile plugins/pre-vibe/scripts/*.py
python3 -m unittest discover -s tests
```
