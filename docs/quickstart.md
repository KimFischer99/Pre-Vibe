# Quickstart

1. Open Claude Code in the project you want to prepare.
2. Enable **Pre-Vibe** from the plugin picker, or just type `/pre-vibe`.
3. Send a rough task, for example:

```text
Help me turn this idea into a build plan.
```

4. Answer any native question dialogs Claude Code opens automatically.
5. Review the generated `PRE_VIBE_SPEC.md`, `CLAUDE.md` or `PROJECT_CLAUDE.md`, and `FIRST_PROMPT.md`.
6. Approve the handoff when Claude Code asks — the next step will be `/clear` then inject `FIRST_PROMPT.md`.
7. After approval, run `/clear` to reset context. Claude Code reads `FIRST_PROMPT.md` and continues from that execution contract.

Pre-Vibe is for the start of a session. It should clarify scope, write durable project context, then hand Claude Code a compact prompt for real work.

## Output Files

| File | Purpose |
| --- | --- |
| `PRE_VIBE_SPEC.md` | Beginner-friendly project handbook with goals, language, evidence, risks, and acceptance criteria. |
| `CLAUDE.md` | Created only when the project has no root agent guidance. |
| `PROJECT_CLAUDE.md` | Reviewable proposal when the project already has root `CLAUDE.md`. |
| `FIRST_PROMPT.md` | Compact execution contract for Claude Code after handoff approval. |
| `PROJECT_INDEX.md` | Architect-only project index for high-uncertainty work. |
