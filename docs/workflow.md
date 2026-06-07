# Workflow Contract

Pre-Vibe has one job: prepare the first session before implementation starts. The workflow is intentionally strict because partial startup is worse than no startup.

## Mandatory Order

1. Call `prepare_project_start`.
2. If `question_request` is present, call `open_question_dialog`.
3. Build the requested project documents.
4. Call `write_project_starting_documents`.
5. Ask the user to approve the `FIRST_PROMPT.md` handoff.
6. After approval, read and inject `FIRST_PROMPT.md` as the active execution contract.

Codex must not stop after writing files. The document write step returns `AWAITING_APPROVAL` and a required handoff contract so the next action is explicit.

## Completion Rule

A Pre-Vibe run is complete only when one of these is true:

- The user approves the handoff and Codex continues from `FIRST_PROMPT.md`.
- The user rejects the handoff and gives a correction.
- The user explicitly cancels Pre-Vibe.

## Native Question UI

Blocking questions must use Codex native question UI through `open_question_dialog`. If the UI is unavailable, Codex should pause and report that it cannot continue safely instead of printing internal backend fields as chat text.

## Document Independence

`PRE_VIBE_SPEC.md`, `AGENTS.md` or `PROJECT_AGENTS.md`, and `PROJECT_INDEX.md` must be standalone. `FIRST_PROMPT.md` may reference whichever files Codex needs for the handoff.

## Safety Boundaries

- Keep writes inside the active project root.
- Do not write internal intake/status/context payloads to disk.
- Do not silently overwrite an existing root `AGENTS.md`; write `PROJECT_AGENTS.md` instead.
- Redact secret-like values before writing generated artifacts.
