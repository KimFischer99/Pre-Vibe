# pre-vibe Workflow

pre-vibe is a Codex intake workflow. Its job is to prevent a vague first request from
becoming polluted execution context. It must gather only the context needed for the
next correct action, then write task-specific artifacts.

## State Machine

| State | Meaning | Allowed output |
|---|---|---|
| `INTAKE_STARTED` | Initial routing and intensity selection. | Progress update only. |
| `NEEDS_USER_INPUT` | A blocking answer is missing. | Ask questions; keep intake notes in conversation context only. |
| `NEEDS_CONTEXT` | Required context evidence is missing. | Run scans/lookups; keep intake notes in conversation context only. |
| `READY_TO_COMPILE` | Evidence is enough to write final artifacts. | Write three final Markdown files. |
| `AWAITING_APPROVAL` | User reviews artifacts. | Show summary and ask for approval. |
| `READY_TO_INJECT` | User approved. | pre-vibe clears context and injects only `FIRST_PROMPT.md`. |
| `DONE` | Intake has ended. | Leave files on disk. |

Never write the final `FIRST_PROMPT.md` while blocking questions or required context
actions remain open.

Do not write `INTAKE.md`, `PRE_VIBE_INTAKE.md`, or equivalent intake drafts to disk.
Temporary intake notes belong only in the active pre-vibe conversation context.

## Intensity Profiles

| Intensity | Use when | Behavior |
|---|---|---|
| `mini` | General work, simple writing, small research, tiny edits. | Up to 3 blocking questions; no scan/fetch by default. |
| `default` | Normal research or coding tasks. | Up to 5 blocking questions; light allowlist scan; fetch only if useful. |
| `architect` | New projects, refactors, high-risk work, complex research. | Up to 10 blocking questions in staged rounds; broader scan/fetch; fuller handbook. |

These profiles control workflow effort, not strict token limits. The final prompt still
must stay compact and action-oriented.

## Context Acquisition

Use evidence, not placeholders.

- User answers prove intent, scope, permissions, and acceptance criteria.
- Project files prove framework, scripts, conventions, and relevant paths.
- Codex environment checks prove AGENTS/plugin/cache state.
- External sources prove current facts only when the task depends on them.

If the evidence does not exist yet, either acquire it or ask the user. Do not simulate
evidence in the final artifacts.

## Scenario Strategy

### General

Focus on output contract: audience, format, tone, constraints, and done-when. Skip
project scan unless the user names a file or the task is high-risk.

### Research

Create research questions and a source map. External source summaries belong in
reference files or the spec handbook, not in `FIRST_PROMPT.md`.

### Coding

Prefer file pointers over repo summaries. The first prompt should tell Codex what to
read first and what not to touch. Project scan evidence should be concise and path-based.

### Mixed

Separate the research scaffold from the implementation brief. Do not let research
background crowd out the execution prompt.

## Approval And Injection

After `READY_TO_COMPILE`, write:

- `PRE_VIBE_SPEC.md`
- `INIT_AGENTS.md`
- `FIRST_PROMPT.md`

Show the user the meaningful parts of `INIT_AGENTS.md` and `FIRST_PROMPT.md`, then ask
for approval. After approval, pre-vibe executes the clear-context step and the new
session receives only `FIRST_PROMPT.md`.
