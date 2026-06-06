# Context Pyramid

Only the top of the pyramid should enter the new Codex session.

| Level | Content | Default destination |
|---|---|---|
| 0 | Task intent | `FIRST_PROMPT.md` |
| 1 | Current task, hard constraints, done-when | `FIRST_PROMPT.md` |
| 2 | Key assumptions and necessary file/source pointers | `FIRST_PROMPT.md` |
| 3 | Decisions, context index, source map | Reference files |
| 4 | Full handbook spec and durable project guidance | Handbook and project guidance files |
| 5 | Raw references, scan details, long notes | Reference files or not saved |

Rules:

- Do not inject levels 4-5 by default.
- For coding, file pointers beat repo summaries.
- For research, source maps beat long source summaries.
- For general tasks, keep the mandatory scan lightweight and avoid fetch unless risk or
  ambiguity justifies it.
- If a detail does not change Codex's next action, keep it out of `FIRST_PROMPT.md`.
