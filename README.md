# Pre-Vibe

Pre-Vibe is a Codex plugin that turns a rough first message into clean project starting context before the agent begins real work.

It is designed for new Codex users, junior builders, and early product sessions where the first request is short, vague, or missing execution detail. Instead of sending Codex straight into implementation, Pre-Vibe reads safe project context, clarifies only the blocking unknowns, builds task-specific starting documents, and continues with a compact first prompt after approval.

Pre-Vibe is a plugin package, not a bundled skill and not a command-style prompt workflow.

## Install

```bash
codex plugin marketplace add KimFischer99/Pre-Vibe --sparse .agents/plugins --sparse plugins/pre-vibe && codex plugin add pre-vibe@pre-vibe
```

Then start a new Codex thread, open **Plugins**, and make sure **Pre-Vibe** is enabled.

## Quick Start

1. Open Codex in the project you want to prepare.
2. Enable **Pre-Vibe** from the plugin picker.
3. Type a rough request, or choose one of the Pre-Vibe starter prompts.
4. Let Codex read the project and Codex environment first.
5. Answer the native question dialogs if Codex opens them.
6. Review the generated starting context, then approve the handoff.

No command syntax is required. If a Codex surface does not expose native MCP elicitation yet, Pre-Vibe reports that limitation instead of falling back to long chat-form questions.

## What It Builds

Pre-Vibe writes three project-specific Markdown files in the active project:

- `PRE_VIBE_SPEC.md`: a beginner-friendly project handbook with goals, scope, user flow, acceptance criteria, risks, suggestions, and useful project pointers.
- `PROJECT_AGENTS.md`: concise Codex-facing execution guidance that respects global `AGENTS.md`.
- `FIRST_PROMPT.md`: the compact prompt that should be injected after approval.

These files must be custom-written from the user's request, project evidence, environment evidence, and user answers. They must not contain reusable template language or implementation details about Pre-Vibe itself unless the user is explicitly working on Pre-Vibe.

## Workflow

Pre-Vibe follows the same product-first spirit as spec-driven tools such as [github/spec-kit](https://github.com/github/spec-kit): clarify the outcome, preserve project principles, plan the next execution boundary, then let the agent work from a stable prompt. The implementation is different: Pre-Vibe stays inside Codex as a plugin with an MCP companion instead of installing command files or skills.

The normal flow is:

1. Prepare the project start.
2. Read safe local project files and Codex component state.
3. Request native question UI for blocking unknowns.
4. Build the project starting documents.
5. Ask for approval.
6. Clear the working context and inject only the compact first prompt.

## Effort Levels

- `mini`: small ordinary tasks; up to 3 blocking questions.
- `default`: normal research or coding tasks; up to 5 blocking questions.
- `architect`: new products, refactors, or high-uncertainty work; up to 10 blocking questions.

These are workflow effort levels, not strict token budgets.

## Repository Layout

- `.agents/plugins/marketplace.json`: repo marketplace entry used by Codex installation.
- `plugins/pre-vibe/`: distributable Codex plugin package.
- `plugins/pre-vibe/.codex-plugin/plugin.json`: plugin manifest.
- `plugins/pre-vibe/.mcp.json`: bundled MCP server registration.
- `plugins/pre-vibe/scripts/pre_vibe.py`: deterministic workflow utilities.
- `plugins/pre-vibe/scripts/mcp_server.py`: minimal stdio MCP server.
- `architecture.md`: current architecture notes.
- `pre-vibe_PRD.md`: product requirements.

## Development Checks

Validate the plugin package:

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/pre-vibe
python3 -m py_compile plugins/pre-vibe/scripts/pre_vibe.py plugins/pre-vibe/scripts/mcp_server.py
```

Run a code review before distribution:

```bash
codex review --uncommitted
```

The project intentionally does not include automated scenario tests. Workflow quality should be checked in live Codex sessions.

## Safety

Pre-Vibe uses allowlist project scanning and skips secret-like files by default, including environment files, private keys, token stores, database dumps, and production logs. It stores temporary preparation notes only in the active conversation context.

## License

MIT
