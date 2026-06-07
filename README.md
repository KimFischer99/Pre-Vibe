# Pre-Vibe

[![Version](https://img.shields.io/badge/version-v0.1.2-brightgreen)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Pre-Vibe turns a rough first request into **three structured documents** before real work begins. It reads your project safely, asks only what it needs to know, then hands Claude Code a compact execution contract — so every session starts with clear scope, project-aware guidance, and a focused prompt.

> Designed for new Claude Code users, junior builders, and early product sessions where the first request is short, vague, or missing execution detail.

---

## One-Click Install

In Claude Code, type:

```
帮我安装一下这个 plugin：KimFischer99/CC-Pre-Vibe
```

Or install manually:

```bash
# 1. Add the marketplace (one-time)
claude plugin marketplace add https://raw.githubusercontent.com/KimFischer99/CC-Pre-Vibe/main/.claude-plugin/marketplace.json

# 2. Enable auto-update
claude plugin marketplace auto-update --enable pre-vibe

# 3. Install the plugin
claude plugin install pre-vibe@pre-vibe
```

Restart Claude Code, type `/pre-vibe`, and tell it your rough idea.

---

## Quick Start (3 Minutes)

| Step | What happens |
|------|-------------|
| **1.** Type `/pre-vibe` in Claude Code | Plugin activates |
| **2.** Say your rough idea | e.g. "Help me turn this idea into a build plan" |
| **3.** Answer 2-5 questions | Claude Code opens native question dialogs |
| **4.** Review the generated docs | Three files appear in your project |
| **5.** Approve the handoff | `/clear` → inject FIRST_PROMPT.md → real work begins |

---

## What Pre-Vibe Builds

Pre-Vibe writes **three task-specific documents** that together constrain Claude Code's context and improve implementation precision:

| Document | What it does | Why it matters |
|---|---|---|
| `PRE_VIBE_SPEC.md` | Beginner-friendly project handbook — goals, scope, project language, evidence, risks, acceptance criteria | Aligns Claude Code with your domain terminology and success criteria before a single line of code |
| `CLAUDE.md` (or `PROJECT_CLAUDE.md`) | Agent-facing execution rules — constraints, file pointers, operation boundaries, verification requirements | Loaded automatically by Claude Code at session start; prevents scope creep and guides every response |
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

Adjust anytime through the plugin settings:
- Default effort: `auto`, `mini`, `default`, `architect`
- Session effort override
- Architect-only project index toggle
- Claude Code environment inspection toggle

---

## How It Works

1. Detects existing context, `CLAUDE.md` files, and git state
2. Builds a safe project index (skips secrets, `node_modules`, etc.)
3. Resolves effort level and document plan
4. Opens native question UI for unresolved decisions
5. Writes customized starting documents
6. Requests approval — then `/clear` and inject `FIRST_PROMPT.md` as the execution contract

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
