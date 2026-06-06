# Language Policy

Default to `auto`.

- If the raw task is mostly Chinese, write outputs in Chinese with stable English filenames and optional bilingual headings.
- If the raw task is mostly English, write outputs in English.
- If the UI language and input language conflict, prioritize the input language for prose.
- Users can override with `zh`, `en`, or `bilingual`.
- `PRE_VIBE_SPEC.md` should use beginner-friendly prose in the user's language.
- `INIT_AGENTS.md` and `FIRST_PROMPT.md` can use concise agent-facing English section names if that improves Codex execution, but the task details should remain understandable to the user.
