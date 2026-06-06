# Agent Adapter: Codex

pre-vibe v0.4 is Codex-first. Other agent adapters can be added later, but the current
artifact rules should optimize for Codex.

## Codex-Friendly `PROJECT_AGENTS.md`

Use durable instructions that improve repeated work in the project:

- Build, lint, test, and validation commands.
- Directory conventions.
- Generated/vendor/secret paths to avoid.
- Review expectations.
- Project-specific file ownership or naming rules.
- Summary of global AGENTS.md and project AGENTS.md when available.
- Conflict policy with higher-priority instructions.
- No rule that conflicts with, narrows, or weakens global AGENTS.md.
- Component usage notes only when they change how Codex should execute in this project.

Do not add one-off task requirements, tutorial prose, or references to the generated
handbook filename/path.

## Codex-Friendly `FIRST_PROMPT.md`

Use compact sections:

- `Goal`
- `Current Task`
- `Hard Constraints`
- `Key Assumptions`
- `Relevant Context`
- `Done When`
- `Operating Mode`

The prompt should tell Codex what to inspect first, what to avoid, when to ask a
blocking question, and how to report completion.

## Codex Workflow Features

- Clear context only after user approval, then inject the first prompt.
- Inject only `FIRST_PROMPT.md`.
- Reference generated artifacts in `FIRST_PROMPT.md` only when it helps Codex start
  cleanly.
- Let Codex read files on demand instead of pasting long summaries.
- For complex work, ask Codex to start with a short plan before editing.
