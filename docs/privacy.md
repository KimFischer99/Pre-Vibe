# Privacy Notes

Pre-Vibe is local-first. It reads safe project context, inspects limited Codex configuration state, and writes Markdown files into the active project.

## Data Read Locally

- Allowlisted project files and top-level structure.
- Root or global `AGENTS.md` guidance when present.
- Codex plugin and skill state under the current user's Codex-related folders.

Pre-Vibe skips common secret-like files and directories during project scans.

Set `inspect_codex_environment` to `false` through Pre-Vibe settings to disable Codex home, plugin cache, marketplace, and standalone skill inspection for a project.

## Data Written Locally

- `PRE_VIBE_SPEC.md`
- `AGENTS.md` or `PROJECT_AGENTS.md`
- `FIRST_PROMPT.md`
- `PROJECT_INDEX.md` for architect effort
- `.pre-vibe/settings.json` when settings are changed

Generated artifacts are plain Markdown or JSON in the active project. Delete those files to remove local Pre-Vibe output.

## Network

The plugin itself does not run a hosted backend. If Codex gathers online evidence for a task, those sources should be listed as evidence in `PRE_VIBE_SPEC.md`.

## Secrets

Generated artifact text is passed through simple secret-like redaction before writing. Do not intentionally include credentials, tokens, private keys, or production secrets in Pre-Vibe prompts or generated documents.
