# pre-vibe v0.4.0

pre-vibe is a Codex workflow plugin for first-session intake. It helps Codex turn a
rough user request into a clear, project-specific workflow before execution starts.

It is not a prompt rewriter and not a Markdown template generator. The workflow:

1. Classifies the user's request.
2. Chooses `mini`, `default`, or `architect` intensity.
3. Builds a safe project execution index and Codex component index before questions.
4. Asks only blocking questions through Codex's native question/user-input or approval UI.
5. Writes task-specific artifacts.
6. Waits for user approval.
7. Clears context and injects only the compact first prompt.

Slash startup is packaged through `prompts/pre-vibe.md` and `commands/pre-vibe.md`.
Current public Codex docs expose custom slash prompts as prompt commands; the install
script syncs the prompt source into `~/.codex/prompts/pre-vibe.md` so it appears in
the slash command picker on supported Codex surfaces.

## User-Facing Artifacts

- `PRE_VIBE_SPEC.md` - beginner-friendly project handbook for the user's task.
- `PROJECT_AGENTS.md` - durable agent guidance that references global AGENTS rules and
  must not conflict with them.
- `FIRST_PROMPT.md` - the only content intended for the next Codex session.

These files must be custom-written from the user's actual input, project evidence, and
environment state. They must not contain reusable template prose or implementation
details about this plugin.

`PRE_VIBE_SPEC.md` and `PROJECT_AGENTS.md` are standalone. Neither file may mention
the other's filename or path; `FIRST_PROMPT.md` may reference generated files when
that helps Codex start cleanly.

Temporary intake notes are not written as `INTAKE.md` or `PRE_VIBE_INTAKE.md`. They
stay only in the active pre-vibe conversation context until the final artifacts are
ready.

## Intensity

- `mini`: lightweight mandatory project/component indexing; up to 3 blocking questions.
- `default`: light project/component indexing; up to 5 blocking questions.
- `architect`: broader project/component indexing; up to 10 blocking questions in staged rounds.

## Plugin Components

- `.codex-plugin/plugin.json` - Codex plugin manifest.
- `.mcp.json` - optional MCP server companion for routing, scanning, environment
  inspection, and artifact writes.
- `skills/pre-vibe/SKILL.md` - workflow instructions loaded by Codex.
- `skills/pre-vibe/agents/openai.yaml` - Codex-facing invocation metadata.
- `skills/pre-vibe/references/` - progressive-disclosure workflow references.
- `prompts/pre-vibe.md` - slash prompt command source for Codex prompt-command startup.
- `commands/pre-vibe.md` - packaged command source for Codex versions that discover
  plugin command files.
- `scripts/pre_vibe.py` - deterministic workflow utilities.
- `scripts/mcp_server.py` - minimal stdio MCP server for the utilities.
- `scripts/install_slash_prompt.py` - syncs the packaged slash prompt into the Codex
  prompts directory during local deployment.

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
