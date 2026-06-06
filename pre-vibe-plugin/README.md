# pre-vibe v0.3.1

pre-vibe is a Codex workflow plugin for first-session intake. It helps Codex turn a
rough user request into a clear, project-specific workflow before execution starts.

It is not a prompt rewriter and not a Markdown template generator. The workflow:

1. Classifies the user's request.
2. Chooses `mini`, `default`, or `architect` intensity.
3. Asks only blocking questions, using Codex's native question UI when available.
4. Reads safe project and Codex environment context when useful.
5. Writes task-specific artifacts.
6. Waits for user approval.
7. Clears context and injects only the compact first prompt.

## User-Facing Artifacts

- `PRE_VIBE_SPEC.md` - beginner-friendly project handbook for the user's task.
- `INIT_AGENTS.md` - durable agent guidance that references global AGENTS rules and
  must not conflict with them.
- `FIRST_PROMPT.md` - the only content intended for the next Codex session.

These files must be custom-written from the user's actual input, project evidence, and
environment state. They must not contain reusable template prose or implementation
details about this plugin.

Temporary intake notes are not written as `INTAKE.md` or `PRE_VIBE_INTAKE.md`. They
stay only in the active pre-vibe conversation context until the final artifacts are
ready.

## Intensity

- `mini`: up to 3 blocking questions.
- `default`: up to 5 blocking questions.
- `architect`: up to 10 blocking questions in staged rounds.

## Plugin Components

- `.codex-plugin/plugin.json` - Codex plugin manifest.
- `.mcp.json` - optional MCP server companion for routing, scanning, environment
  inspection, and artifact writes.
- `skills/pre-vibe/SKILL.md` - workflow instructions loaded by Codex.
- `skills/pre-vibe/agents/openai.yaml` - Codex-facing invocation metadata.
- `skills/pre-vibe/references/` - progressive-disclosure workflow references.
- `scripts/pre_vibe.py` - deterministic workflow utilities.
- `scripts/mcp_server.py` - minimal stdio MCP server for the utilities.

## Safety

The workflow uses allowlist scanning and skips secrets by default:

- no `.env` values
- no private keys
- no token stores
- no database dumps
- no production logs with personal data

If environment details are needed, the workflow should ask first and only inspect names
or safe metadata.

## Validation

Before distribution, validate the plugin manifest:

```bash
python3 /Users/kimfischer99/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py pre-vibe-plugin
```

The repo intentionally does not include automated test scaffolding for user scenario
quality; real workflow quality should be checked with live Codex sessions.
