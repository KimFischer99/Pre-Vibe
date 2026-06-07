# Troubleshooting

## Plugin Does Not Appear

1. Restart the Codex thread after installing.
2. Confirm the marketplace was added.
3. Reinstall the plugin after version changes.
4. Check that `plugins/pre-vibe/.codex-plugin/plugin.json` is present.

## MCP Tools Do Not Load

Run:

```bash
python3 -m py_compile plugins/pre-vibe/scripts/*.py
```

If `python3` is missing, install Python 3 or use WSL on Windows.

## Native Question UI Does Not Open

Pre-Vibe should pause instead of printing backend fields. Restart the thread, enable the plugin again, and retry. If the UI still fails, reduce the task to a smaller first prompt or run without Pre-Vibe for that session.

## Documents Are Generated But Codex Stops

This is a workflow failure. The expected next step is:

1. Ask the user to approve the `FIRST_PROMPT.md` handoff.
2. Read `FIRST_PROMPT.md` after approval.
3. Continue from its execution contract.

The MCP write result includes `handoff.required_next_actions` to make this sequence explicit.

## Validation Commands

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/pre-vibe
python3 -m py_compile plugins/pre-vibe/scripts/*.py
python3 -m unittest discover -s tests
codex review --uncommitted
```
