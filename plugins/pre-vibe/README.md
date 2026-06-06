# Pre-Vibe Plugin Package

This directory is the distributable Codex plugin package for Pre-Vibe.

Pre-Vibe is MCP-backed. It does not register bundled skills and does not install command-style prompt files. Users enable it from the Codex plugin picker, then start with a rough task or one of the plugin starter prompts.

## Components

- `.codex-plugin/plugin.json`: Codex plugin manifest.
- `.mcp.json`: bundled MCP server registration.
- `scripts/pre_vibe.py`: deterministic project-start workflow helpers.
- `scripts/mcp_server.py`: stdio MCP server exposing those helpers to Codex.
- `LICENSE`: package license.

## Runtime Behavior

The MCP server exposes product-facing tools that:

- prepare a project start from a rough user request;
- scan only safe project metadata and allowlisted files;
- inspect global and project Codex guidance plus installed components;
- request Codex native question UI through MCP elicitation when blocking answers are needed;
- write the final project starting documents after Codex has authored task-specific content.

Tool results use short user-visible status text such as "正在构建项目初始文档。". Detailed workflow state is returned as structured content for Codex, not as chat prose.

## Documents Written

When the workflow is ready, Codex writes:

- `PRE_VIBE_SPEC.md`
- `PROJECT_AGENTS.md`
- `FIRST_PROMPT.md`

The package only writes content Codex has already authored for the user's actual task. It must not generate reusable template prose.

## Validation

From the repository root:

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/pre-vibe
python3 -m py_compile plugins/pre-vibe/scripts/pre_vibe.py plugins/pre-vibe/scripts/mcp_server.py
```
