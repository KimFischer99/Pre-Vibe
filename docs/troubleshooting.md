# Troubleshooting

## Plugin Does Not Appear

1. Restart the Claude Code session after installing.
2. Run `/reload-plugins` to pick up changes.
3. Confirm the plugin is enabled with `/plugin list`.
4. Check that `plugins/pre-vibe/.claude-plugin/plugin.json` is present.

## MCP Tools Do Not Load

Run:

```bash
python3 -m py_compile plugins/pre-vibe/scripts/*.py
```

If `python3` is missing, install Python 3 or use WSL on Windows.

## Tools Use The Wrong Project Root

Plugin MCP tools use `CLAUDE_PROJECT_DIR` as the default project root. Claude Code sets this variable to the active project directory when it starts the plugin server.

If Pre-Vibe scans or writes in the wrong place:

1. Start Claude Code from the intended project root.
2. Restart the session or run `/reload-plugins`.
3. Pass an explicit `project` or `project_root` argument when testing MCP tools directly.

## Native Question UI Does Not Open

Pre-Vibe should pause instead of printing backend fields. Restart the session, enable the plugin again, and retry. If the UI still fails, reduce the task to a smaller first prompt or run without Pre-Vibe for that session.

## Documents Are Generated But Claude Code Stops

This is a workflow failure. The expected next step is:

1. Ask the user to approve the `FIRST_PROMPT.md` handoff.
2. Read `FIRST_PROMPT.md` after approval.
3. Continue from its execution contract.

The MCP write result includes `handoff.required_next_actions` to make this sequence explicit.

## Validation Commands

```bash
claude plugin validate plugins/pre-vibe --strict
python3 -m py_compile plugins/pre-vibe/scripts/*.py
python3 -m unittest discover -s tests
```
