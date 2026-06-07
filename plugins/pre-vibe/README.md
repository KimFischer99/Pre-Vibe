# Pre-Vibe Plugin Package

This directory is the distributable Claude Code plugin package for Pre-Vibe v0.1.3.

Pre-Vibe is backed by a local stdio MCP server and plugin-scoped workflow guidance. Users enable it from the Claude Code plugin picker, then start with a rough task or starter prompt.

## Components

- `.claude-plugin/plugin.json`: Claude Code plugin manifest.
- `.mcp.json`: bundled MCP server registration.
- `skills/pre-vibe/SKILL.md`: workflow guidance for Claude Code orchestration.
- `scripts/pre_vibe.py`: compatibility facade and CLI.
- `scripts/mcp_server.py`: stdio MCP server.
- `scripts/pv_*.py`: focused workflow modules.
- `LICENSE`: package license.

## Runtime Behavior

The MCP server exposes tools that prepare project starts, inspect safe local context, read Claude Code guidance, manage effort settings, request native question UI, and write Claude Code-authored starting documents. Project-relative defaults resolve through `CLAUDE_PROJECT_DIR`, while bundled scripts are referenced through `CLAUDE_PLUGIN_ROOT`.

Tool results use short user-visible status text such as "正在构建项目初始文档。". Detailed workflow state is returned as structured content for Claude Code.

`write_project_starting_documents` is not the final workflow step. After it writes files, Claude Code must request user approval for `FIRST_PROMPT.md`; after approval, Claude Code must read and inject `FIRST_PROMPT.md` as the execution contract.

## Developer CLI

`scripts/pre_vibe.py` is not the normal user entrypoint. It is a compatibility facade for the MCP server imports and a small local CLI for inspecting routing decisions during development:

```bash
python3 plugins/pre-vibe/scripts/pre_vibe.py --task "fix login" --project . --no-scan
```

Use `/pre-vibe` in Claude Code for the real plugin workflow.

## Documents Written

- `PRE_VIBE_SPEC.md`
- `CLAUDE.md` or `PROJECT_CLAUDE.md`
- `FIRST_PROMPT.md`
- `PROJECT_INDEX.md` for architect effort

## Validation

From the repository root:

```bash
claude plugin validate plugins/pre-vibe --strict
python3 -m py_compile plugins/pre-vibe/scripts/*.py
python3 -m unittest discover -s tests
```
