# Workflow Contract

Pre-Vibe has one job: prepare the first session before implementation starts. The workflow is intentionally strict because partial startup is worse than no startup.

## Mandatory Order

1. Call `prepare_project_start`.
2. The result contains `question_request` — Claude Code opens native question UI automatically.
   Do not call any MCP tool for questions.
3. Call `write_project_starting_documents`.
4. Ask the user to review and approve `FIRST_PROMPT.md`.
   Explain that after approval, the next steps are: `/clear` → inject `FIRST_PROMPT.md`.
5. After approval, ask the user to run `/clear`, then read and inject `FIRST_PROMPT.md` as the active execution contract.

Claude Code must not stop after writing files. The document write step returns `AWAITING_APPROVAL` and a required handoff contract so the next action is explicit.

## Completion Rule

A Pre-Vibe run is complete only when one of these is true:

- The user approves the handoff, runs `/clear`, and Claude Code continues from `FIRST_PROMPT.md`.
- The user rejects the handoff and gives a correction.
- The user explicitly cancels Pre-Vibe.

## Native Question UI

Blocking questions are returned as structured `question_request` in the `prepare_project_start` result. Claude Code opens the native question UI automatically. If the UI is unavailable, Claude Code should pause and report that it cannot continue safely instead of printing internal backend fields as chat text.

## Document Independence

`PRE_VIBE_SPEC.md`, `CLAUDE.md` or `PROJECT_CLAUDE.md`, and `PROJECT_INDEX.md` must be standalone. `FIRST_PROMPT.md` may reference whichever files Claude Code needs for the handoff.

## Safety Boundaries

- Keep writes inside the active project root.
- Do not write internal intake/status/context payloads to disk.
- Do not silently overwrite an existing root `CLAUDE.md`; write `PROJECT_CLAUDE.md` instead.
- Redact secret-like values before writing generated artifacts.
