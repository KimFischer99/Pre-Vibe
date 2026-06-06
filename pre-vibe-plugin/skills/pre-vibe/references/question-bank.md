# Blocking Question Rules

pre-vibe does not ask from a static questionnaire. It asks only when the answer changes
execution.

## Blocking If It Changes

- Architecture or technical approach.
- Data model, schema, storage, or permissions.
- External dependency, API, platform, or deployment target.
- User-facing behavior or UX contract.
- Acceptance criteria or definition of done.
- Scope boundaries.
- Irreversible or high-risk operation.
- Authorization, especially for reverse analysis or third-party systems.

## Do Not Ask

- Preference questions that can be handled by a conservative default.
- Curiosity questions.
- Questions answerable from files or environment.
- Questions already answered in the user's wording.
- Open-ended brainstorming that does not narrow execution.

## Intensity Limits

| Intensity | Question behavior |
|---|---|
| `mini` | Ask up to 3 blocking questions. |
| `default` | Ask up to 5 blocking questions. |
| `architect` | Ask up to 10 blocking questions in short staged rounds; stop when the next action is clear. |

Use Codex's native question/user-input UI when available. It should display the
questions and let the user answer in the normal input surface. If that UI is
unavailable, ask concise direct questions in chat.

## Reverse Or Desktop Targets

If a user asks to reverse, decompile, inspect, or analyze "the thing on my desktop" but
does not provide a target path, ask for:

- Exact absolute path.
- File/app name and type if known.
- Confirmation that the user is authorized to analyze it.
- Analysis boundaries and forbidden actions.

Do not proceed to a final prompt until these are known or explicitly declined.
