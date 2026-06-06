# Intensity Profiles

This file remains for compatibility with older references. v0.3 no longer treats token
counts as strict budgets. Use intensity profiles to control workflow effort, then keep
the first prompt minimal.

| Intensity | Behavior |
|---|---|
| `mini` | Up to 3 blocking questions; no project scan or fetch by default. |
| `default` | Up to 5 blocking questions; light allowlist scan; fetch only when useful. |
| `architect` | Up to 10 blocking questions in staged rounds; broader scan/fetch; full handbook when the task needs it. |

Compression rule for `FIRST_PROMPT.md`:

1. Remove rationale.
2. Remove examples.
3. Collapse background into assumptions.
4. Replace summaries with file/source pointers.
5. Narrow the current task.
