# Pre-Vibe

[![Version](https://img.shields.io/badge/version-v0.1.1-brightgreen)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Pre-Vibe is a Claude Code plugin for preparing a new session before real work begins. It turns a rough first message into project-specific starting context, guided questions, AGENTS.md-compatible guidance, and a compact execution prompt.

It is designed for new Claude Code users, junior builders, and early product sessions where the first request is short, vague, or missing execution detail. Pre-Vibe reads safe project context, checks Claude Code guidance, asks only blocking questions, writes starting documents, and hands Claude Code a concise first prompt after approval.

## Install

### From Community Marketplace

```bash
claude plugin install pre-vibe@claude-community
```

### Local Development

```bash
claude --plugin-dir ./plugins/pre-vibe
```

After installation, start a new Claude Code session and enable **Pre-Vibe** from the plugin picker.

## Quick Start

1. Open Claude Code in the project you want to prepare.
2. Enable **Pre-Vibe** from the plugin picker.
3. Type a rough request such as "Help me turn this idea into a build plan."
4. Answer the native question dialogs when Claude Code opens them.
5. Review the generated starting documents.
6. Approve the handoff so Claude Code can continue from `FIRST_PROMPT.md`.

## What It Builds

Pre-Vibe writes task-specific Markdown in the active project:

- `PRE_VIBE_SPEC.md`: a beginner-friendly handbook with goals, scope, project language, evidence, acceptance criteria, risks, and next steps.
- `AGENTS.md`: created when the project has no root agent guidance.
- `PROJECT_AGENTS.md`: created as a reviewable proposal when a root `AGENTS.md` already exists.
- `FIRST_PROMPT.md`: a compact execution contract for Claude Code, fully rewritten on each handoff.
- `PROJECT_INDEX.md`: architect effort only; an index of project intent, resources, tools, files, environment, and purpose.

`PRE_VIBE_SPEC.md`, the agent guidance document, and `PROJECT_INDEX.md` stay independent. `FIRST_PROMPT.md` may reference the files Claude Code should use for the handoff.

## Effort Levels

Pre-Vibe can choose effort automatically, and users can adjust it through plugin settings tools.

- `mini`: small ordinary tasks; up to 3 blocking questions.
- `default`: normal research or coding tasks; up to 5 blocking questions.
- `architect`: new products, refactors, high-uncertainty work; up to 10 blocking questions and `PROJECT_INDEX.md`.

Settings available through the plugin:

- default effort: `auto`, `mini`, `default`, or `architect`
- session effort override
- architect-only project index toggle
- auto-upgrade behavior
- Claude Code environment inspection toggle

## Workflow

Pre-Vibe follows a session-start workflow:

1. Detect existing Pre-Vibe documents, AGENTS.md files, and git state.
2. Build a safe project and Claude Code environment index.
3. Resolve effort level and document output plan.
4. Ask native UI questions for unresolved blocking decisions.
5. Capture local and online evidence for `PRE_VIBE_SPEC.md`.
6. Build customized starting documents.
7. Ask the user to approve the `FIRST_PROMPT.md` handoff.
8. After approval, read and inject `FIRST_PROMPT.md` as the execution contract.

Document generation is preparation, not completion. A Pre-Vibe run is only complete after the user approves the handoff and Claude Code continues from `FIRST_PROMPT.md`, or after the user explicitly cancels.

## Architecture

The plugin package lives in `plugins/pre-vibe/` and includes:

- `.claude-plugin/plugin.json`: plugin manifest
- `.mcp.json`: bundled stdio MCP server registration
- `skills/pre-vibe/SKILL.md`: plugin-scoped workflow guidance
- `scripts/mcp_server.py`: MCP tool surface
- `scripts/pv_*.py`: focused workflow modules for routing, scanning, questions, settings, artifacts, and compact output

The MCP server returns short user-visible status text and structured workflow data for Claude Code. The Python layer provides deterministic routing, validation, scanning, settings, and safe writing; Claude Code authors the final task-specific Markdown.

## File Structure

```text
pre-vibe/
├── .github/
│   └── workflows/ci.yml
├── docs/
│   ├── installation.md
│   ├── quickstart.md
│   ├── troubleshooting.md
│   └── workflow.md
├── plugins/pre-vibe/
│   ├── .claude-plugin/plugin.json
│   ├── .mcp.json
│   ├── README.md
│   ├── scripts/
│   └── skills/pre-vibe/SKILL.md
├── tests/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── PRIVACY.md
└── README.md
```

## Documentation

- [Installation](docs/installation.md)
- [Quickstart](docs/quickstart.md)
- [Workflow contract](docs/workflow.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Privacy & Security](PRIVACY.md)

## Development Checks

```bash
claude plugin validate plugins/pre-vibe
python3 -m py_compile plugins/pre-vibe/scripts/*.py
python3 -m unittest discover -s tests
```

## Safety

Pre-Vibe uses allowlist project scanning, skips secret-like files, keeps output paths inside the active project, and avoids silently overwriting existing root `AGENTS.md`.

## License

MIT
