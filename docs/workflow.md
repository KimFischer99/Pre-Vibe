# Workflow Contract

Pre-Vibe has one job: prepare the first session before implementation starts. The workflow is intentionally strict because partial startup is worse than no startup.

## Mandatory Order

1. Call `prepare_project_start`.
2. The result contains `question_request` — Claude Code opens native question UI automatically.
   Do not call any MCP tool for questions.
3. Call `write_project_starting_documents`.
4. Present `FIRST_PROMPT.md` for user review — wait for explicit approval like a plan audit.
   Do not proceed without user confirmation.
5. After explicit approval: execute `/clear`, then read and inject `FIRST_PROMPT.md` as the active execution contract. Begin real implementation work immediately.

The `/clear` and prompt injection are performed **by Claude Code**, not by the user. This is a strict rule. The user's only role in this step is auditing and approving the generated documents.

Claude Code must not stop after writing files. The document write step returns `AWAITING_APPROVAL` and a required handoff contract so the next action is explicit.

## Completion Rule

A Pre-Vibe run is complete only when one of these is true:

- The user explicitly approves the handoff, Claude Code executes `/clear`, and continues from `FIRST_PROMPT.md`.
- The user rejects the handoff and gives a correction.
- The user explicitly cancels Pre-Vibe.

## Native Question UI

Blocking questions are returned as structured `question_request` in the `prepare_project_start` result. Claude Code opens the native question UI automatically. If the UI is unavailable, Claude Code should pause and report that it cannot continue safely instead of printing internal backend fields as chat text.

## Document Independence

`PRE_VIBE_SPEC.md`, `CLAUDE.md` or `PROJECT_CLAUDE.md`, and `PROJECT_INDEX.md` must be standalone. `FIRST_PROMPT.md` may reference whichever files Claude Code needs for the handoff.

## Document Content Rules

- `PRE_VIBE_SPEC.md` is an engineering execution handbook, NOT a background knowledge encyclopedia.
- Focus on: env vars, language/framework stack, installed plugins & skills, project component inventory, git state, past session context, actionable integration suggestions.
- Avoid: generic tech introductions, industry overviews, Wikipedia-style background information.
- Every suggestion must be actionable and tied to a concrete engineering decision.

## Safety Boundaries

- Keep writes inside the active project root.
- Do not write internal intake/status/context payloads to disk.
- Do not silently overwrite an existing root `CLAUDE.md`; write `PROJECT_CLAUDE.md` instead.
- Redact secret-like values before writing generated artifacts.
