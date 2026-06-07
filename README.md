# Pre-Vibe

[![Version](https://img.shields.io/badge/version-v0.1.2-brightgreen)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Pre-Vibe turns a rough first request into **three structured documents** before real work begins. It reads your project safely, asks only what it needs to know, then hands Claude Code a compact execution contract — so every session starts with clear scope, project-aware guidance, and a focused prompt.

> Designed for new Claude Code users, junior builders, and early product sessions where the first request is short, vague, or missing execution detail.

---

## Quick Install

Tell Claude Code:

```
请帮我安装这个 plugin：git clone https://github.com/KimFischer99/CC-Pre-Vibe.git ~/.claude/plugins/marketplaces/pre-vibe && claude plugin install pre-vibe@pre-vibe
```

Or run manually:

```bash
# Step 1: Clone the repo as a directory marketplace (do this once)
git clone https://github.com/KimFischer99/CC-Pre-Vibe.git ~/.claude/plugins/marketplaces/pre-vibe

# Step 2: Install the plugin
claude plugin install pre-vibe@pre-vibe

# Step 3 (optional): Update later with
cd ~/.claude/plugins/marketplaces/pre-vibe && git pull
```

After installation, restart Claude Code, type `/pre-vibe`, and tell it your rough idea.

---

## Quick Start

| Step | What you do | What Claude Code does |
|------|------------|----------------------|
| **1.** Type `/pre-vibe` | Describe your rough task | Plugin activates and scans your project |
| **2.** Answer questions | Pick answers in the native question dialogs | Asks only what's needed for scope clarity |
| **3.** Review documents | Check PRE_VIBE_SPEC.md, CLAUDE.md, FIRST_PROMPT.md | Writes three task-specific files to your project |
| **4.** Approve the handoff | Confirm FIRST_PROMPT.md meets your expectations | Runs `/clear` → injects FIRST_PROMPT.md → begins real work |

---

## What Pre-Vibe Builds

Pre-Vibe writes **three task-specific documents** that together constrain Claude Code's context and improve implementation precision:

| Document | What it does | Why it matters |
|---|---|---|
| `PRE_VIBE_SPEC.md` | Engineering execution handbook — env vars, stack, plugins, skills, component inventory, git state, integration suggestions | Aligns Claude Code with your project reality before a single line of code; focuses on execution, not background knowledge |
| `CLAUDE.md` (or `PROJECT_CLAUDE.md`) | Agent-facing execution rules — constraints, file pointers, operation boundaries, verification gates | Loaded automatically by Claude Code at session start; prevents scope creep and guides every response |
| `FIRST_PROMPT.md` | Compact execution contract with Completion Contract, stop/ask conditions, and verification gates | The only prompt after handoff — keeps Claude Code focused on the deliverable, not the setup |

> `PROJECT_INDEX.md` is also available at **architect** effort level for high-uncertainty work.

These three documents work together to **constrain large-model context, reduce hallucination, and keep Claude Code on track** — especially important for non-English prompts, complex projects, or sessions with limited token budgets.

---

## Effort Levels

| Level | Questions | Best for |
|-------|-----------|----------|
| **mini** | ≤ 3 | Small changes, quick fixes, simple research |
| **default** | ≤ 5 | Normal coding or research tasks |
| **architect** | ≤ 10 + PROJECT_INDEX.md | New products, refactors, high-uncertainty work |

Adjust anytime through the plugin settings, or use the `set_effort_level` tool.

---

## How It Works

1. Detects existing Pre-Vibe documents, `CLAUDE.md` files, env vars, installed plugins/skills, git state, and past session context
2. Builds a safe project index (skips secrets, node_modules, etc.)
3. Resolves effort level and document output plan
4. Opens native question UI for unresolved blocking decisions
5. Writes customized starting documents focused on engineering execution
6. Presents FIRST_PROMPT.md for user audit — after explicit approval, `/clear` and inject

---

## Architecture

```
plugins/pre-vibe/
├── .claude-plugin/plugin.json     # Plugin manifest
├── .mcp.json                      # stdio MCP server
├── skills/pre-vibe/SKILL.md       # Workflow guidance
├── scripts/
│   ├── mcp_server.py              # MCP tool surface
│   ├── pre_vibe.py                # CLI / compatibility facade
│   ├── pv_*.py                    # Routing, scan, questions, settings, artifacts
│   └── pyproject.toml             # Python project config
└── README.md
```

The Python layer handles deterministic routing, scanning, validation, and safe writing. Claude Code authors the final task-specific Markdown using MCP tool results and structured workflow data.

---

## Documentation

- [Quickstart](docs/quickstart.md)
- [Workflow contract](docs/workflow.md)
- [Installation](docs/installation.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Privacy & Security](PRIVACY.md)

---

## Safety

- Allowlist project scanning — only reads safe filenames and suffixes
- Skips secrets, keys, tokens, databases, logs
- Keeps output paths inside the active project
- Never silently overwrites existing root `CLAUDE.md`

---

## Development

```bash
claude plugin validate plugins/pre-vibe
python3 -m py_compile plugins/pre-vibe/scripts/*.py
python3 -m unittest discover -s tests
```

## License

MIT
