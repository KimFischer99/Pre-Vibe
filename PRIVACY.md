# Privacy & Security

Pre-Vibe is a local-first Claude Code plugin. It does not provide a hosted service or send plugin data to a Pre-Vibe backend.

## Data Read Locally

- Allowlisted project files and top-level structure.
- Root or global `AGENTS.md` guidance when present.
- Claude Code plugin and skill state under the current user's `~/.claude/` folder.

Pre-Vibe skips common secret-like files and directories during project scans.

Set `inspect_codex_environment` to `false` through Pre-Vibe settings to disable Claude Code home, plugin cache, marketplace, and standalone skill inspection for a project.

## Data Written Locally

- `PRE_VIBE_SPEC.md`
- `AGENTS.md` or `PROJECT_AGENTS.md`
- `FIRST_PROMPT.md`
- `PROJECT_INDEX.md` for architect effort
- `.pre-vibe/settings.json` when settings are changed

Generated artifacts are plain Markdown or JSON in the active project. Delete those files to remove local Pre-Vibe output.

## Network

The plugin itself does not run a hosted backend. If Claude Code gathers online evidence for a task, those sources should be listed as evidence in `PRE_VIBE_SPEC.md`.

## Secrets

Generated artifact text is passed through simple secret-like redaction before writing. Do not intentionally include credentials, tokens, private keys, or production secrets in Pre-Vibe prompts or generated documents.

## Reporting Security Concerns

Please do not post secrets, private repositories, proprietary binaries, or sensitive project output in public issues.

For security concerns, use GitHub's private vulnerability reporting flow if it is enabled for this repository. If private reporting is unavailable, open a public issue with a minimal description that does not include sensitive data, and the maintainer can move the discussion to a safer channel.

## Supported Versions

Only the latest commit on `main` is supported during this early plugin phase.
