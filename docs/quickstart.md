# Quickstart

1. Open Codex in the project you want to prepare.
2. Enable **Pre-Vibe** from the plugin picker.
3. Send a rough task, for example:

```text
Help me turn this idea into a build plan.
```

4. Answer any native question dialogs Codex opens.
5. Review the generated `PRE_VIBE_SPEC.md`, `AGENTS.md` or `PROJECT_AGENTS.md`, and `FIRST_PROMPT.md`.
6. Approve the handoff when Codex asks.
7. Codex reads `FIRST_PROMPT.md` and continues from that execution contract.

Pre-Vibe is for the start of a session. It should clarify scope, write durable project context, then hand Codex a compact prompt for real work.

## Output Files

| File | Purpose |
| --- | --- |
| `PRE_VIBE_SPEC.md` | Beginner-friendly project handbook with goals, language, evidence, risks, and acceptance criteria. |
| `AGENTS.md` | Created only when the project has no root agent guidance. |
| `PROJECT_AGENTS.md` | Reviewable proposal when the project already has root `AGENTS.md`. |
| `FIRST_PROMPT.md` | Compact execution contract for Codex after handoff approval. |
| `PROJECT_INDEX.md` | Architect-only project index for high-uncertainty work. |
