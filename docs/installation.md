# Installation

Pre-Vibe is distributed as a Claude Code plugin package from this repository.

## From This Marketplace

```bash
claude plugin marketplace add KimFischer99/CC-Pre-Vibe
claude plugin install pre-vibe@pre-vibe
```

If the marketplace is already configured, run only the install command.

## Local Development Install

When developing from a clone, use the `--plugin-dir` flag:

```bash
claude --plugin-dir ./plugins/pre-vibe
```

This loads the plugin directly without requiring installation. Run `/reload-plugins` to pick up changes without restarting.

## Supported Platforms

| Platform | Status | Notes |
| --- | --- | --- |
| macOS | Supported | Requires `python3` on PATH. |
| Linux | Supported | Requires `python3` on PATH. |
| Windows with WSL | Supported | Run Claude Code and the plugin inside WSL. |
| Windows native | Experimental | Use WSL if `python3` or stdio MCP startup is unreliable. |

## Verify

```bash
claude plugin validate plugins/pre-vibe --strict
python3 -m py_compile plugins/pre-vibe/scripts/*.py
python3 -m unittest discover -s tests
```
