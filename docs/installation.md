# Installation

Pre-Vibe is distributed as a local Codex plugin package from this repository.

## Beginner Path

Ask Codex from any project:

```text
Help me install the Pre-Vibe plugin from KimFischer99/Pre-Vibe into Codex.
```

Codex can run the plugin marketplace commands and explain the prompts.

## Manual Install

From Codex, add the repository marketplace and install the plugin:

```bash
codex plugin marketplace add KimFischer99/Pre-Vibe --sparse .agents/plugins --sparse plugins/pre-vibe
codex plugin add pre-vibe@pre-vibe
```

Start a new Codex thread, open **Plugins**, and enable **Pre-Vibe**.

## Local Development Install

When developing from a clone, use the repo-local marketplace entry:

```bash
codex plugin marketplace add ./ --sparse .agents/plugins --sparse plugins/pre-vibe
codex plugin add pre-vibe@pre-vibe
```

If Codex still loads an older cached copy, remove and reinstall the plugin from the plugin picker or run the install command again after changing the version.

## Supported Platforms

| Platform | Status | Notes |
| --- | --- | --- |
| macOS | Supported | Requires `python3` on PATH. |
| Linux | Supported | Requires `python3` on PATH. |
| Windows with WSL | Supported | Run Codex and the plugin inside WSL. |
| Windows native | Experimental | Use WSL if `python3` or stdio MCP startup is unreliable. |

## Verify

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/pre-vibe
python3 -m py_compile plugins/pre-vibe/scripts/*.py
python3 -m unittest discover -s tests
```
